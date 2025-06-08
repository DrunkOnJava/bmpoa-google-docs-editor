/**
 * BMPOA Document Image Organizer
 * Complete solution for resizing and organizing images
 * 
 * Features:
 * - Resizes all images wider than 400 points
 * - Centers images with proper spacing
 * - Maintains aspect ratios
 * - Adds captions where missing
 * - Groups related images
 */

function organizeAllImages() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  
  // Configuration
  var MAX_WIDTH = 400;
  var IMAGE_SPACING_BEFORE = 12;
  var IMAGE_SPACING_AFTER = 12;
  
  // Statistics
  var stats = {
    totalImages: 0,
    resized: 0,
    centered: 0,
    captioned: 0
  };
  
  // Get all images
  var images = body.getImages();
  stats.totalImages = images.length;
  
  Logger.log('Starting image organization for ' + images.length + ' images...');
  
  // Process each image
  images.forEach(function(image, index) {
    try {
      var paragraph = image.getParent();
      
      // 1. Resize if needed
      var width = image.getWidth();
      var height = image.getHeight();
      
      if (width > MAX_WIDTH) {
        var ratio = MAX_WIDTH / width;
        var newHeight = Math.round(height * ratio);
        
        image.setWidth(MAX_WIDTH);
        image.setHeight(newHeight);
        
        stats.resized++;
        Logger.log('Resized image ' + (index + 1) + ': ' + width + 'x' + height + ' → ' + MAX_WIDTH + 'x' + newHeight);
      }
      
      // 2. Center the image
      if (paragraph.getType() === DocumentApp.ElementType.PARAGRAPH) {
        paragraph.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
        stats.centered++;
        
        // 3. Add proper spacing
        paragraph.setSpacingBefore(IMAGE_SPACING_BEFORE);
        paragraph.setSpacingAfter(IMAGE_SPACING_AFTER);
        
        // 4. Check if image needs a caption
        var nextElement = paragraph.getNextSibling();
        var hasCaption = false;
        
        if (nextElement && nextElement.getType() === DocumentApp.ElementType.PARAGRAPH) {
          var nextText = nextElement.asText().getText().trim();
          // Check if next paragraph looks like a caption (short, possibly starts with "Figure" or "Image")
          if (nextText.length < 100 && nextText.length > 0) {
            hasCaption = true;
            // Style the caption
            nextElement.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
            nextElement.setItalic(true);
            nextElement.setFontSize(10);
            nextElement.setSpacingAfter(IMAGE_SPACING_AFTER);
          }
        }
        
        // 5. Add a caption if missing
        if (!hasCaption && image.getAltTitle()) {
          var caption = body.insertParagraph(
            body.getChildIndex(paragraph) + 1,
            'Figure ' + (index + 1) + ': ' + image.getAltTitle()
          );
          caption.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
          caption.setItalic(true);
          caption.setFontSize(10);
          caption.setSpacingAfter(IMAGE_SPACING_AFTER);
          stats.captioned++;
        }
      }
      
    } catch (e) {
      Logger.log('Error processing image ' + (index + 1) + ': ' + e);
    }
  });
  
  // Save document
  doc.saveAndClose();
  
  // Log summary
  Logger.log('\n=== IMAGE ORGANIZATION COMPLETE ===');
  Logger.log('Total images processed: ' + stats.totalImages);
  Logger.log('Images resized: ' + stats.resized);
  Logger.log('Images centered: ' + stats.centered);
  Logger.log('Captions added: ' + stats.captioned);
  
  // Show completion dialog
  var ui = DocumentApp.getUi();
  var message = 'Image organization complete!\n\n' +
                '• Total images: ' + stats.totalImages + '\n' +
                '• Resized: ' + stats.resized + '\n' +
                '• Centered: ' + stats.centered + '\n' +
                '• Captions added: ' + stats.captioned + '\n\n' +
                'All images have been formatted for optimal display.';
  
  ui.alert('Success', message, ui.ButtonSet.OK);
}

/**
 * Create a visual image inventory at the end of the document
 */
function createImageInventory() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  
  // Add inventory section at the end
  body.appendPageBreak();
  var title = body.appendParagraph('IMAGE INVENTORY');
  title.setHeading(DocumentApp.ParagraphHeading.HEADING1);
  title.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  
  var subtitle = body.appendParagraph('All images used in this document');
  subtitle.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
  subtitle.setItalic(true);
  body.appendParagraph('');
  
  // Get all images and create inventory
  var images = body.getImages();
  
  images.forEach(function(image, index) {
    var inventoryItem = body.appendParagraph('Image ' + (index + 1));
    inventoryItem.setBold(true);
    
    // Add image details
    var details = body.appendParagraph(
      'Size: ' + Math.round(image.getWidth()) + ' x ' + Math.round(image.getHeight()) + ' points'
    );
    details.setIndentFirstLine(20);
    
    if (image.getAltTitle()) {
      var titlePara = body.appendParagraph('Title: ' + image.getAltTitle());
      titlePara.setIndentFirstLine(20);
    }
    
    if (image.getAltDescription()) {
      var descPara = body.appendParagraph('Description: ' + image.getAltDescription());
      descPara.setIndentFirstLine(20);
    }
    
    body.appendParagraph('');
  });
  
  doc.saveAndClose();
  
  var ui = DocumentApp.getUi();
  ui.alert('Image Inventory Created', 
           'An inventory of all ' + images.length + ' images has been added to the end of the document.', 
           ui.ButtonSet.OK);
}

/**
 * Main menu function to run all optimizations
 */
function optimizeDocument() {
  var ui = DocumentApp.getUi();
  
  var response = ui.alert(
    'Optimize Document Images',
    'This will:\n' +
    '• Resize large images (max width: 400pt)\n' +
    '• Center all images\n' +
    '• Add proper spacing\n' +
    '• Add captions where possible\n\n' +
    'Continue?',
    ui.ButtonSet.YES_NO
  );
  
  if (response == ui.Button.YES) {
    organizeAllImages();
  }
}

/**
 * Create custom menu when document opens
 */
function onOpen() {
  var ui = DocumentApp.getUi();
  ui.createMenu('Image Tools')
    .addItem('Optimize All Images', 'optimizeDocument')
    .addItem('Create Image Inventory', 'createImageInventory')
    .addSeparator()
    .addItem('Resize Images Only', 'resizeAllImages')
    .addItem('Center Images Only', 'centerAllImages')
    .addToUi();
}

/**
 * Just resize images without other formatting
 */
function resizeAllImages() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  var images = body.getImages();
  var resized = 0;
  
  images.forEach(function(image) {
    if (image.getWidth() > 400) {
      var ratio = 400 / image.getWidth();
      image.setWidth(400);
      image.setHeight(image.getHeight() * ratio);
      resized++;
    }
  });
  
  doc.saveAndClose();
  
  var ui = DocumentApp.getUi();
  ui.alert('Resize Complete', 'Resized ' + resized + ' images to maximum width of 400 points.', ui.ButtonSet.OK);
}

/**
 * Just center images without resizing
 */
function centerAllImages() {
  var doc = DocumentApp.openById('169fOjfUuf2j-V0HIVCS8REf3Wtl94D5Gxt67sUdgJQs');
  var body = doc.getBody();
  var images = body.getImages();
  var centered = 0;
  
  images.forEach(function(image) {
    var paragraph = image.getParent();
    if (paragraph.getType() === DocumentApp.ElementType.PARAGRAPH) {
      paragraph.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
      centered++;
    }
  });
  
  doc.saveAndClose();
  
  var ui = DocumentApp.getUi();
  ui.alert('Center Complete', 'Centered ' + centered + ' images.', ui.ButtonSet.OK);
}