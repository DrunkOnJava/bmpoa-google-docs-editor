
function resizeAllImages() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  var images = body.getImages();
  
  Logger.log('Found ' + images.length + ' images');
  
  images.forEach(function(image, index) {
    var width = image.getWidth();
    var height = image.getHeight();
    
    if (width > 400) {
      var ratio = 400 / width;
      var newHeight = height * ratio;
      
      image.setWidth(400);
      image.setHeight(newHeight);
      
      Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → 400x' + newHeight);
    }
  });
  
  doc.saveAndClose();
}
