# Wood Texture Asset Setup Guide

## 📁 Upload Location
Place all 4 image files in:
```
C:\edgettstest\LECTRA\ui\src\assets\images\
```

## 🖼️ Required Files

### 1. darkest_wood.png
- **Usage**: Navbar background
- **Requirements**: 
  - Square dimensions (recommended: 512x512 or 1024x1024)
  - Seamless/tileable pattern
  - Dark wood texture
- **Current fallback**: Solid color #2d2d2d

### 2. dark_wood.png
- **Usage**: Main content area backgrounds
- **Requirements**: 
  - Square dimensions (recommended: 512x512 or 1024x1024)
  - Seamless/tileable pattern
  - Medium-dark wood texture
- **Current fallback**: Solid color #3d3d3d

### 3. light_wood.png
- **Usage**: Card/panel backgrounds
- **Requirements**: 
  - Square dimensions (recommended: 512x512 or 1024x1024)
  - Seamless/tileable pattern
  - Light wood texture
- **Current fallback**: Solid color #f5f5f5

### 4. title.png
- **Usage**: LECTRA logo in hero section
- **Requirements**: 
  - Any dimensions (will scale automatically)
  - Transparent background recommended
  - High resolution for crisp display
- **Current fallback**: Text "LECTRA"

## 🔄 How It Works

### Automatic Fallback System
- If images are **not present**: Uses solid color fallbacks
- If images are **present**: Uses wood textures with color fallback during load
- If image **fails to load**: Falls back to solid color gracefully

### Wood Texture Tiling
- Textures repeat seamlessly across the surface
- Tile size: 256x256px (adjustable in styles.css if needed)
- Larger source images (512x512 or 1024x1024) provide better quality

## 📝 After Upload
1. Place all 4 files in the images folder
2. **Refresh the browser** (or hot reload will trigger automatically)
3. Wood textures will appear immediately
4. Logo will replace text automatically

## 🎨 Customization
To adjust tile size, edit `ui/src/styles.css`:
```css
.bg-darkest-wood {
  background-size: 256px 256px; /* Change this value */
}
```

## ✅ Verification
Once uploaded, you should see:
- Textured navbar instead of solid dark gray
- Wood grain in main content areas
- Your LECTRA logo in the hero section
- Consistent seamless tiling across all surfaces
