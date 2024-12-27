import io
import openai
import requests

openai = openai.OpenAI()


class ChatConnector:
  # Factory class for entity wrappers.

  OPENAI_MODEL = "gpt-4o"

  TOOLS = [{"type": "file_search"}, {"type": "code_interpreter"}]

  ##############################
  # Assistants
  ##############################

  # Create an assistant.
  @classmethod
  def create_assistant(cls, **kwargs):
    return openai.beta.assistants.create(
        name=kwargs.get("name"),
        description=kwargs.get("description", None),
        instructions=kwargs.get("instructions", None),
        metadata=kwargs.get("metadata", {}),
        model=cls.OPENAI_MODEL,
        tools=cls.TOOLS,
        tool_resources=kwargs.get("tool_resources", None),
    )

  # Delete resources associated with the given assistant.
  @staticmethod
  def delete_assistant(self, assistant_id):
    openai.beta.assistants.delete(assistant_id)

  ##############################
  # Threads
  ##############################

  # Create a thread.
  @staticmethod
  def create_thread(**kwargs):
    messages = [msg.to_json() for msg in kwargs["messages"]] if "messages" in kwargs else None

    # Return a ChatThread wrapper.
    return ChatThread(
        openai.beta.threads.create(
            messages=messages,
            metadata=kwargs.get("metadata", {}),
        ))

  # Retrieve a thread by ID.
  @staticmethod
  def retrieve_thread(thread_id):
    # Return a ChatThread wrapper.
    return ChatThread(openai.beta.threads.retrieve(thread_id))

  # Delete resources associated with this thread.
  @staticmethod
  def delete_thread(thread_id):
    return openai.beta.threads.delete(thread_id)

  ##############################
  # Files
  ##############################

  # Upload a file.
  @classmethod
  def upload_file(cls, file_path, purpose="assistants"):
    with open(file_path, "rb") as f:
      return openai.files.create(file=f, purpose=purpose)

  # Upload a string as a file.
  @classmethod
  def upload_string(cls, str, purpose="assistants"):
    return cls.upload_bytes(str.encode("utf-8"), purpose)

  # Upload a byte array as a file.
  @classmethod
  def upload_bytes(cls, bytes, purpose="assistants"):
    return openai.files.create(file=io.BytesIO(bytes), purpose=purpose)

  # Delete a file.
  @classmethod
  def delete_file_by_id(cls, file_id):
    return openai.files.delete(file_id)


class ChatThread:
  # Wrapper class for OpenAI Thread.

  def __init__(self, thread):
    self.thread = thread

  @property
  def id(self):
    return self.thread.id

  @property
  def metadata(self):
    return self.thread.metadata

  # Retrieve this thread's messages.
  def list_messages(self, **kwargs):
    return openai.beta.threads.messages.list(thread_id=self.id, **kwargs)

  # Update this thread's metadata.
  def update_metadata(self, metadata):
    return openai.beta.threads.update(self.id, metadata=metadata)

  # Submit the thread to the assistant and wait for a reply.
  def get_assistant_reply(self, assistant_id):

    # Create a run and wait for it to finish.
    run = openai.beta.threads.runs.create_and_poll(
        assistant_id=assistant_id,
        thread_id=self.thread.id,
    )
    if run.status != "completed":
      raise Exception(f"run {run.id} not complete ({run.status})")

    # Extract messages related to the run.
    assistant_messages = filter(lambda message: message.role == "assistant",
                                self.list_messages(run_id=run.id))
    reply_text = "\n".join(m.content[0].text.value for m in assistant_messages)
    return reply_text


class ChatMessage:
  # A text message, possibly also with attachments, in the form of previously uploaded files.

  def __init__(self, content, role="user"):
    self.content = content
    self.role = role
    self.attachments = []

  def add_file_id(self, file_id):
    self.attachments.append(file_id)

  def to_json(self):

    json = {
        "role": self.role,
        "content": self.content,
    }

    def format_attachment(file_id):
      return {
          "file_id": file_id,
          "tools": [{
              "type": "code_interpreter"
          }],
      }

    if len(self.attachments):
      json.update({
          "attachments": [format_attachment(file_id) for file_id in self.attachments],
      })

    return json

  def add_to_thread(self, thread):
    json = self.to_json()
    return openai.beta.threads.messages.create(thread.id, **json)
