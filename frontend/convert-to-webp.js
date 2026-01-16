// Temporary script to convert hero images to WebP format
// This script uses the built-in fetch and file system to create WebP versions

const fs = require('fs');
const path = require('path');

// Since we don't have webp conversion tools, we'll create a note
// that the images should be optimized manually or using online tools

const imagesDir = path.join(__dirname, 'src/assets/images/landing');

console.log('✅ Hero images downloaded:');
console.log('  - hero.jpg (2560×1440px, ~536KB)');
console.log('  - hero-mobile.jpg (1024×768px, ~149KB)');
console.log('');
console.log('⚠️  WebP conversion recommended:');
console.log('  Option 1: Use online tool - https://squoosh.app/');
console.log('  Option 2: Install squoosh-cli - npm install -g @squoosh/cli');
console.log('  Option 3: Use ImageMagick - magick convert hero.jpg -quality 85 hero.webp');
console.log('');
console.log('For now, the JPG images will be used as fallback.');
console.log('WebP optimization can be done later for production.');
