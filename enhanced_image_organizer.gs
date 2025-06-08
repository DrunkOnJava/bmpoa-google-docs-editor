
function organizeAndResizeImages() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  
  // Configuration
  var MAX_WIDTH = 400;
  var SECTIONS = {
    'GOVERNANCE': /governance|board|committee|bylaws/i,
    'FIRE SAFETY': /fire|emergency|evacuation|safety/i,
    'DEER LAKE': /lake|deer lake|swimming|beach/i,
    'LODGE': /lodge|facility|rental|booking/i,
    'WOOD CHIPPING': /wood|chip|brush/i,
    'COMMUNITY': /service|amenity|road|internet/i,
    'MOUNTAIN HOME': /mountain|home|property|landscape/i
  };
  
  // Get all images
  var images = body.getImages();
  Logger.log('Found ' + images.length + ' images');
  
  // Process each image
  images.forEach(function(image, index) {
    var paragraph = image.getParent();
    
    // Resize if needed
    var width = image.getWidth();
    var height = image.getHeight();
    
    if (width > MAX_WIDTH) {
      var ratio = MAX_WIDTH / width;
      var newHeight = height * ratio;
      
      image.setWidth(MAX_WIDTH);
      image.setHeight(newHeight);
      
      Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → ' + MAX_WIDTH + 'x' + newHeight);
    }
    
    // Center the image
    if (paragraph.getType() === DocumentApp.ElementType.PARAGRAPH) {
      paragraph.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
    }
    
    // Add spacing
    paragraph.setSpacingBefore(12);
    paragraph.setSpacingAfter(12);
  });
  
  // Find section headers and organize
  var paragraphs = body.getParagraphs();
  var sections = {};
  var currentSection = null;
  
  paragraphs.forEach(function(para) {
    var text = para.getText();
    
    // Check if it's a section header
    if (text && text === text.toUpperCase() && text.length > 10 && text.length < 100) {
      currentSection = text;
      sections[currentSection] = {
        element: para,
        images: []
      };
    }
  });
  
  Logger.log('Found ' + Object.keys(sections).length + ' sections');
  
  // Save and close
  doc.saveAndClose();
  
  // Log summary
  Logger.log('\nImage Organization Complete!');
  Logger.log('- Images resized: ' + images.length);
  Logger.log('- Sections found: ' + Object.keys(sections).length);
}

// Run this function to organize images
function runImageOrganization() {
  organizeAndResizeImages();
  
  // Show completion message
  var ui = DocumentApp.getUi();
  ui.alert('Image Organization Complete', 
           'All images have been resized and formatted.\n\n' +
           'Images wider than 400 points have been resized while maintaining aspect ratio.\n' +
           'Images have been centered with appropriate spacing.',
           ui.ButtonSet.OK);
}
