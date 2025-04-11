import json
import openai
import time
from pprint import pp
from db import db
from models.ThreadRecord import ThreadRecord

# openai.debug = True
openai_api = openai.OpenAI()


def resolve_function(function_name):
  # Not yet implemented
  raise ValueError(f"No such function: {function_name}")


class AiAssistantError(Exception):
  pass


class AiAssistantFactory:
  """
    Factory class for wrapper types for using Assistants, a feature of the OpenAI API.
    Thread IDs are recorded along with their contexts in the db, because they are not
    searchable through OpenAI.
  """

  DEFAULT_OPENAI_MODEL = "gpt-4o"

  def __init__(self, openai_model=DEFAULT_OPENAI_MODEL):
    self.openai_model = openai_model
    self.attachments = []

  def delete_attachments(self):
    for attachment in self.attachments:
      self.delete_file_by_id(attachment)

  ##############################
  # Assistants
  ##############################

  class AssistantWrapper:
    """
      Wrapper class for OpenAI Assistant.
      It is not necessary to persist Assistant IDs in the database, as a listing of the
      Assistants associated with an account may be obtained via the API.
    """

    def __init__(self, factory, assistant):
      self.factory = factory
      self.assistant = assistant  # The OpenAI API Assistant object.
      self.deleted = False

    @property
    def id(self):
      return self.assistant.id

    @property
    def metadata(self):
      return self.assistant.metadata

    def get_reply(self, thread, instructions=None):
      """
        Submit a thread to the assistant and wait for a reply.
        parameters:
          thread    A thread wrapper (which contains an API object and a database object)
      """
      thread_id = thread.thread_handle_id

      # Create a run.
      run = openai_api.beta.threads.runs.create(assistant_id=self.id,
                                                thread_id=thread_id,
                                                additional_instructions=instructions)

      # Poll run for completion, handle intermediate requests for action.
      while run.status not in ["completed", "cancelled"]:
        print(f'waiting for run {run.id}')
        time.sleep(1)
        run = openai_api.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(f'got {run.status}')
        if run.status == "failed":
          error_message = run.last_error.message or "Unknown error"
          raise Exception(f"run {run.id} failed: {error_message}")
        if run.status == "requires_action":
          self._take_action(run, thread_id)

      # Grab all messages from the assistant.
      assistant_messages = list(
          filter(lambda message: message.run_id == run.id and message.role == "assistant",
                 thread.list_messages()))

      # Concatenate messages.
      reply_text = "\n".join(m.content[0].text.value for m in assistant_messages)
      return reply_text

    # Handle function calls.
    @staticmethod
    def _take_action(run, thread_id):
      for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        function_args = tool_call.function.arguments
        print("call", function_name, function_args)
        func = resolve_function(function_name)
        try:
          function_args = json.loads(function_args)
        except Exception as e:  # Hack around an extra } at end of JSON string.
          if function_args.endswith("}"):
            function_args = function_args[:-1]
            function_args = json.loads(function_args)
          else:
            raise e
        function_result_str = func(**function_args)
        openai.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=[{
                "tool_call_id": tool_call.id,
                "output": function_result_str,
            }],
        )

    def delete(self):
      """ Delete resources associated with this assistant. """
      if not self.deleted:
        openai_api.beta.assistants.delete(self.id)
        self.assistant = None
        self.deleted = True

  def assistant_builder(self):
    """
      Create an assistant, using the builder pattern.
      Assistant properties:
        name              The topic name
        version           The version of this assistant's configuration
        description       A description (for whom?)
        instructions      Text for the assistant outlining the assistant's role and behavior.
        metadata          A dictionary of arbitrary key(str), value(str) pairs.
        file_ids          A list of uploaded files to feed into the assistant's code interpreter.
    """

    class AssistantBuilder:

      def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.description = None
        self.instructions = None
        self.metadata = None
        self.functions = []

      def set_name(self, name):
        self.name = name
        return self  # for chaining

      def set_description(self, description):
        self.description = description
        return self  # for chaining

      def set_instructions(self, instructions):
        self.instructions = instructions
        return self  # for chaining

      def set_metadata(self, key, value):
        if self.metadata is None:
          self.metadata = {}
        self.metadata[key] = value
        return self  # for chaining

      def add_function(self, function_name):
        # Validate the function.
        func = resolve_function(function_name)
        self.functions.append(func)

      def build(self):
        #print(f"Building assistant {self.name} {self.metadata}")
        if self.name is None:
          raise ValueError("name must be provided")
        if self.instructions is None:
          raise ValueError("instructions must be provided")

        args = dict(
            name=self.name,
            description=self.description,
            metadata=self.metadata,
            model=self.factory.openai_model,
            tools=[{
                "type": "code_interpreter"
            }] + [f.get_json() for f in self.functions],
        )
        print(f"Building assistant {args}")

        assistant = openai_api.beta.assistants.create(**args)

        return self.factory.AssistantWrapper(self.factory, assistant)

    return AssistantBuilder(self)

  def find_assistant_by_metadata(self, **kwargs):
    """ Retrieve an assistant by its metadata properties. """

    def has_all_metadata_props(asst):
      for key, value in kwargs.items():
        if not asst.metadata or not asst.metadata.get(key) == value:
          return False
      return True

    try:
      for asst in openai_api.beta.assistants.list():
        if has_all_metadata_props(asst):
          return self.AssistantWrapper(self, asst)
    except openai.APIStatusError as e:
      self.raise_api_error(e)

  def list_assistants(self):
    return [self.AssistantWrapper(self, asst) for asst in openai_api.beta.assistants.list()]

  def delete_assistant_by_id(self, asst_id):
    openai_api.beta.assistants.delete(asst_id)

  ##############################
  # Threads
  ##############################

  class ThreadWrapper:
    """ Wrapper class for OpenAI Thread. """

    def __init__(self, thread_record, thread_handle):
      self.thread_record = thread_record  # What we're calling the database object.
      self.thread_handle = thread_handle  # What we're calling the API object.

    @property
    def id(self):
      return self.thread_record.id  # Use the database ID

    @property
    def thread_handle_id(self):
      return self.thread_handle.id  # The OpenAI ID.

    @property
    def metadata(self):
      return self.thread.metadata

    def list_messages(self):
      """  Retrieve this thread's messages. """
      messages = openai_api.beta.threads.messages.list(thread_id=self.thread_handle_id)
      return messages.data

    def update_metadata(self, metadata):
      """ Update this thread's metadata. """
      return openai_api.beta.threads.update(self.id, metadata=metadata)

    def delete(self):
      """ Delete resources associated with this thread. """
      if not self.deleted:
        openai_api.beta.threads.delete(self.thread_handle_id)
        self.thread_handle = None
        self.thread_record.deleted = True
        db.session.add(self.thread_record)
        db.session.commit()

    @property
    def deleted(self):
      return self.thread_record.deleted

  def thread_builder(self):
    """
      Create a thread (using builder pattern)
      Thread properties:
        topic       The
        user_id     The ID of the user of this thread in the consumer application.
        metadata    A dictionary of key(str), value(str) pairs.
        messages    A list of initial messages in this thread.
    """

    class ThreadBuilder:

      def __init__(self, factory):
        self.factory = factory
        self.topic = None
        self.user_id = None
        self.metadata = None
        self.messages = []

      def set_topic(self, topic):
        self.topic = topic
        return self  # for chaining

      def set_user_id(self, user_id):
        self.user_id = user_id
        return self  # for chaining

      def set_metadata(self, key, value):
        if self.metadata is None:
          self.metadata = {}
        self.metadata[key] = value
        return self  # for chaining

      def add_message(message_wrapper):
        self.messages.append(message_wrapper.to_json())

      def build(self):
        if self.topic is None:
          raise ValueError("topic must be provided")
        if self.user_id is None:
          raise ValueError("user_id must be provided")

        thread_kwargs = {}
        thread_kwargs["metadata"] = self.metadata

        if self.messages:
          thread_kwargs["messages"] = self.messages

        thread_handle = openai_api.beta.threads.create(**thread_kwargs)

        thread_record = ThreadRecord(thread_id=thread_handle.id,
                                     topic=self.topic,
                                     user_id=self.user_id)
        db.session.add(thread_record)
        db.session.commit()

        return self.factory.ThreadWrapper(thread_record, thread_handle)

    return ThreadBuilder(self)

  def retrieve_thread(self, thread_id):
    """ Retrieve a thread by its database ID. """
    thread_record = ThreadRecord.query.filter_by(id=thread_id).first()
    if not thread_record:
      raise ValueError(f"thread {thread_id} is not found")
    if thread_record.deleted:
      raise ValueError("that thread was deleted")
    thread_handle = openai_api.beta.threads.retrieve(thread_record.thread_id)
    return self.ThreadWrapper(thread_record, thread_handle)

  def find_thread(self, topic, user_id):
    """ Find a thread given its metadata. """
    thread_record = ThreadRecord.query.filter_by(topic=topic, user_id=user_id,
                                                 deleted=False).first()
    if not thread_record:
      return None
    try:
      thread_handle = openai_api.beta.threads.retrieve(thread_record.thread_id)
    except openai.NotFoundError:
      thread_record.deleted = True
      db.session.add(thread_record)
      db.session.commit()
      return None

    return self.ThreadWrapper(thread_record, thread_handle)

  ##############################
  # Messages
  ##############################

  class MessageWrapper:
    """
      A user message.  Always has text.  May also have attached files, which the caller must 
      upload using one of the uploader methods of the factory. 
    """

    def __init__(self, factory, text, role="user"):
      self.factory = factory
      self.text = text
      self.role = role
      self.attachments = []

    def attach_file_by_id(self, file_id):
      self.attachments.append(file_id)
      self.factory.attachments.append(file_id)
      return self

    def to_json(self):

      def format_attachment(file_id):
        return {
            "file_id": file_id,
            "tools": [{
                "type": "code_interpreter"
            }],
        }

      attachments = [format_attachment(file_id) for file_id in self.attachments]

      return {
          "role": self.role,
          "content": self.text,
          "attachments": attachments or None,
      }

    def add_to_thread(self, thread):
      thread_handle_id = thread.thread_handle_id
      json = self.to_json()
      openai_api.beta.threads.messages.create(thread_handle_id, **json)

  def user_message(self, text):
    """
      Create a user message.
      parameters:
        text        Message text.
    """
    return self.MessageWrapper(self, text, role="user")

  def system_message(self, text):
    """
      Create a system message.
      parameters:
        text        Message text.
    """
    return self.MessageWrapper(self, text, role="system")

  ##############################
  # Files
  ##############################

  # Upload a file.
  @classmethod
  def upload_file(cls, file_path, purpose="assistants"):
    with open(file_path, "rb") as f:
      return cls.upload_bytes(f, purpose)

  # Upload a string as a file.
  @classmethod
  def upload_string(cls, str, purpose="assistants"):
    return cls.upload_bytes(str.encode("utf-8"), purpose)

  # Upload a byte array as a file.
  @classmethod
  def upload_bytes(cls, file, purpose="assistants"):
    return openai_api.files.create(file=file, purpose=purpose)

  # Delete a file.
  @classmethod
  def delete_file_by_id(cls, file_id):
    return openai_api.files.delete(file_id)

  ##############################
  # Pull it together
  ##############################

  @staticmethod
  def raise_api_error(openai_api_error):
    error_message = (openai_api_error.message
                     or (openai_api_error.body and openai_api_error.body.get("message"))
                     or "API Error")
    raise AiAssistantError(error_message) from open_api_error

  def open_chat(self, config):
    version = "".join(config.get("version", []))
    if not version:
      raise ValueError("version required")
    topic = config.get("topic", "")
    if not topic:
      raise ValueError("topic required")
    user_id = config.get("user_id", "")

    def create_or_reuse_assistant():
      assistant_created = False
      assistant = self.find_assistant_by_metadata(topic=topic, version=version)
      if assistant is None:

        assistant_description = "\n".join(config.get("description", []))
        assistant_instructions = "\n".join(config.get("instructions", []))
        if not assistant_instructions:
          raise ValueError("missing assistant instructions")
        assistant_functions = config.get("functions", [])

        assistant_builder = (self.assistant_builder().set_name(topic).set_description(
            assistant_description).set_instructions(assistant_instructions).set_metadata(
                "topic", topic).set_metadata("version", version))
        for f in assistant_functions:
          assistant_builder.add_function(f)
        assistant = assistant_builder.build()

        assistant_created = True

      return assistant, assistant_created

    def create_or_continue_thread():
      thread = factory.find_thread(topic=topic, user_id=user_id)
      thread_created = False
      # TODO: continuing a thread is temporarily disabled.
      if thread:
        thread.delete()
        thread = None
      if thread is None:
        thread = factory.thread_builder().set_topic(topic).set_user_id(user_id).build()
        thread_created = True
      return thread, thread_created

    assistant, assistant_created = create_or_reuse_assistant()
    thread, thread_created = create_or_continue_thread()

    if thread_created:
      run_instructions = ("\n".join(config["first_run_instructions"])
                          if "first_run_instructions" in config else None)
    else:
      factory.user_message("What's next?").add_to_thread(thread)
      run_instructions = "The user was distracted. Remind them why we are here and what to do next."

    reply = assistant.get_reply(thread, instructions=run_instructions)

    factory.delete_attachments()

    return assistant, thread, reply

  def continue_chat(self, thread_id, user_message):
    factory = AssistedChatFactory()
    thread = factory.retrieve_thread(thread_id)
    topic = thread.thread_record.topic
    assistant = self.find_assistant_by_metadata(topic=topic)
    if not assistant:
      raise ValueError(f"No assistant for topic={topic}?")

    factory.user_message(user_message).add_to_thread(thread)
    reply = assistant.get_reply(thread)
    return assistant, thread, reply

  def close_chat(self, thread_id):
    thread = factory.retrieve_thread(thread_id)
    thread.delete()
