function showSidebar() {
  var html = HtmlService.createHtmlOutputFromFile('Sidebar')
      .setTitle('Domofile');
  SpreadsheetApp.getUi().showSidebar(html);
}

function getDriveFiles() {
  var folder = DriveApp.getFolderById('your_drive_folder_id');
  var files = folder.getFiles();
  var fileList = [];
  
  while (files.hasNext()) {
    var file = files.next();
    fileList.push({
      name: file.getName(),
      url: file.getUrl()
    });
  }
  return fileList;
}

