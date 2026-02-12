# Test Fixtures

This directory contains test assets used by E2E tests.

## Image Files

For photo upload tests, you can use the following test images:

### test-image.jpg
- **Purpose**: Generic test photo for upload functionality
- **Size**: ~100 KB (suitable for quick uploads)
- **Dimensions**: 800x600px
- **Format**: JPEG

### test-image-large.jpg
- **Purpose**: Test photo for testing file size limits
- **Size**: ~5 MB (near max upload limit)
- **Dimensions**: 4000x3000px
- **Format**: JPEG

### test-image-small.jpg
- **Purpose**: Thumbnail test
- **Size**: ~10 KB
- **Dimensions**: 200x150px
- **Format**: JPEG

## Creating Test Images

If test images are not present, they can be generated programmatically or downloaded from public domain sources like:
- https://picsum.photos/ (Lorem Picsum - placeholder images)
- https://unsplash.com/license (Free to use images)

For automated test image generation, use Playwright's screenshot functionality:

```typescript
// In a test setup file
const page = await browser.newPage();
await page.goto('https://picsum.photos/800/600');
await page.screenshot({ path: 'tests/fixtures/test-image.jpg' });
```

## JSON Fixtures

JSON fixtures for backend integration tests are located in:
`backend/tests/fixtures/`

- `users.json` - Sample user data
- `trips.json` - Sample trip data
- `tags.json` - Sample tag data
