# 🖼️ BMPOA Document Image Action Plan

## Current Situation
- **15 total images** in the document
- **12 images clustered** at the beginning (indices 2-13)
- **All images missing captions**
- **12 images oversized** (468pt width, need to be 400pt)
- **Poor distribution** - images need to be spread throughout relevant sections

## 🎯 Immediate Actions Required

### For AGENT 1 (Backend):
1. **Execute Image Resize** (NOW)
   ```bash
   # Run the Apps Script to resize all images
   # This will resize 12 images from 468pt → 400pt width
   ```

2. **Create Image Movement API**
   ```python
   POST /api/v1/document/{id}/move-image
   {
     "image_id": "kix.xxxxx",
     "target_section": "FIRE SAFETY",
     "position": "after_paragraph_50"
   }
   ```

3. **Section Mapping API**
   ```python
   GET /api/v1/document/{id}/sections-with-indices
   # Returns each section with its character indices for precise placement
   ```

### For AGENT 2 (Frontend):
1. **Image Management Dashboard**
   - Grid view of all 15 images
   - Drag-drop to reorder
   - Section assignment dropdown
   - Caption editor for each image

2. **Visual Section Map**
   - Show document sections as drop zones
   - Preview where images will be placed
   - Real-time updates via WebSocket

## 📍 Specific Image Placement Plan

### Images 1-2 (Mountain/Landscape views)
- **Current**: Indices 2-3
- **Move to**: "II. A MOUNTAIN HOME" section
- **Reason**: These appear to be scenic mountain views

### Images 3-5 (Maps/Boundaries)  
- **Current**: Indices 4-6
- **Move to**: "I. GOVERNANCE & STRUCTURE" 
- **Reason**: Likely property boundaries or organizational maps

### Images 6-8 (Emergency/Safety related)
- **Current**: Indices 7-9
- **Move to**: "IV. FIRE SAFETY & EMERGENCY PREPAREDNESS"
- **Reason**: Could be evacuation routes or safety diagrams

### Images 9-12 (Recreation/Amenities)
- **Current**: Indices 10-13
- **Move to**: "VI. DEER LAKE RECREATION AREA"
- **Reason**: Likely lake or facility photos

### Image 13 (Virginia State Flag)
- **Current**: Index 3552
- **Action**: Keep in place, add caption
- **Caption**: "Virginia State Flag - Blue Mountain is located in Virginia"

### Images 14-15 (Mountain Views)
- **Current**: Indices 15308, 15310
- **Action**: Keep at end as closing images
- **Captions**: Add descriptive mountain view captions

## 🔄 Coordination Workflow

1. **AGENT 1 runs resize script** → All images reduced to 400pt width
2. **AGENT 2 builds UI** → Image management interface ready
3. **Both agents coordinate** → Move images via API + UI
4. **AGENT 2 adds captions** → Through caption editor
5. **AGENT 1 applies changes** → Batch update to document

## 📊 Success Metrics

- [ ] All 15 images ≤ 400pt width
- [ ] No more than 2 consecutive images
- [ ] Each major section has relevant images
- [ ] All images have descriptive captions
- [ ] Images are centered with 12pt spacing

## 🚀 Let's Start!

AGENT 1: Ready to execute the resize script and create the movement API
AGENT 2: Ready to build the image management dashboard

Who goes first?