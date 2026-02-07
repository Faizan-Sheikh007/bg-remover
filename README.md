# Background Removal API

Flask-based API for removing backgrounds from images, changing backgrounds, and creating passport photo grids.

## Features

- ✅ AI-powered background removal (using rembg)
- ✅ Background color replacement
- ✅ Passport photo grid generation
- ✅ High-quality image processing

## Deploy to Render

### Step 1: Push to GitHub

1. Create a new GitHub repository
2. Push these files:
   - `app.py`
   - `requirements.txt`
   - `render.yaml`
   - `runtime.txt`
   - `.gitignore`

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Click **"Create Web Service"**

### Step 3: Configuration (Optional)

If you want to manually configure instead of using `render.yaml`:

- **Name**: background-removal-api
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Instance Type**: Free (or paid for better performance)

### Step 4: Get Your API URL

After deployment, Render will provide a URL like:
```
https://background-removal-api.onrender.com
```

## API Endpoints

### 1. Health Check
```
GET /health
```

### 2. Remove Background
```
POST /remove-background
Content-Type: multipart/form-data

Body:
- image: (file)
```

### 3. Change Background
```
POST /change-background
Content-Type: application/json

Body:
{
  "image": "data:image/png;base64,...",
  "background_color": "#FFFFFF"
}
```

### 4. Create Passport Grid
```
POST /create-passport-grid
Content-Type: application/json

Body:
{
  "image": "data:image/png;base64,...",
  "cols": 4,
  "rows": 4,
  "photo_width": 413,
  "photo_height": 531
}
```

## Laravel Integration

### Install Guzzle (if not already installed)
```bash
composer require guzzlehttp/guzzle
```

### Example Laravel Service

```php
<?php

namespace App\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use Illuminate\Support\Facades\Log;

class BackgroundRemovalService
{
    private $client;
    private $apiUrl;

    public function __construct()
    {
        $this->apiUrl = env('BACKGROUND_REMOVAL_API_URL', 'https://your-render-app.onrender.com');
        $this->client = new Client([
            'base_uri' => $this->apiUrl,
            'timeout' => 60,
        ]);
    }

    public function removeBackground($imagePath)
    {
        try {
            $response = $this->client->post('/remove-background', [
                'multipart' => [
                    [
                        'name' => 'image',
                        'contents' => fopen($imagePath, 'r'),
                        'filename' => basename($imagePath)
                    ]
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            return $data['image'] ?? null;
        } catch (GuzzleException $e) {
            Log::error('Background removal failed: ' . $e->getMessage());
            return null;
        }
    }

    public function changeBackground($base64Image, $backgroundColor = '#FFFFFF')
    {
        try {
            $response = $this->client->post('/change-background', [
                'json' => [
                    'image' => $base64Image,
                    'background_color' => $backgroundColor
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            return $data['image'] ?? null;
        } catch (GuzzleException $e) {
            Log::error('Background change failed: ' . $e->getMessage());
            return null;
        }
    }

    public function createPassportGrid($base64Image, $cols = 4, $rows = 4)
    {
        try {
            $response = $this->client->post('/create-passport-grid', [
                'json' => [
                    'image' => $base64Image,
                    'cols' => $cols,
                    'rows' => $rows,
                    'photo_width' => 413,
                    'photo_height' => 531
                ]
            ]);

            $data = json_decode($response->getBody(), true);
            return $data['image'] ?? null;
        } catch (GuzzleException $e) {
            Log::error('Passport grid creation failed: ' . $e->getMessage());
            return null;
        }
    }

    public function healthCheck()
    {
        try {
            $response = $this->client->get('/health');
            return json_decode($response->getBody(), true);
        } catch (GuzzleException $e) {
            return ['status' => 'error', 'message' => $e->getMessage()];
        }
    }
}
```

### Add to .env
```env
BACKGROUND_REMOVAL_API_URL=https://your-render-app.onrender.com
```

### Example Controller Usage

```php
<?php

namespace App\Http\Controllers;

use App\Services\BackgroundRemovalService;
use Illuminate\Http\Request;

class ImageController extends Controller
{
    private $bgRemovalService;

    public function __construct(BackgroundRemovalService $bgRemovalService)
    {
        $this->bgRemovalService = $bgRemovalService;
    }

    public function removeBackground(Request $request)
    {
        $request->validate([
            'image' => 'required|image|max:10240'
        ]);

        $image = $request->file('image');
        $result = $this->bgRemovalService->removeBackground($image->getRealPath());

        if ($result) {
            return response()->json([
                'success' => true,
                'image' => $result
            ]);
        }

        return response()->json([
            'success' => false,
            'message' => 'Background removal failed'
        ], 500);
    }
}
```

## Important Notes

⚠️ **Free Tier Limitations**:
- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-60 seconds
- Consider upgrading to paid tier for production use

🚀 **Performance Tips**:
- Use paid Render instance for better performance
- Consider adding Redis caching for frequently processed images
- Implement request queuing for bulk operations

## Troubleshooting

If deployment fails:
1. Check Render logs for errors
2. Ensure all dependencies are in `requirements.txt`
3. Verify Python version compatibility
4. Check memory usage (rembg requires ~1GB RAM)

## License

MIT
"# bg-remover" 
