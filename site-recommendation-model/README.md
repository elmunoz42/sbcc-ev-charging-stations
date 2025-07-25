# Street View Image Collection for EV Charging Station Site Analysis

This module collects Google Street View images in a systematic grid pattern around Orcutt, California to support computer vision analysis for identifying optimal EV charging station locations.

## Overview

The script collects street view images that can be analyzed for diagonal parking availability - a key criterion for accessible EV charging station placement. It creates a grid covering approximately 5 square miles around coordinates 34.865838, -120.447520 (Orcutt, CA).

## Files

- `street_view_collector.py` - Main collection script with StreetViewCollector class
- `example_usage.py` - Example usage and test scripts
- `config_template.py` - Configuration template
- `requirements.txt` - Python dependencies
- `site_data/` - Output directory for collected images and metadata

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Key dependencies include:

- `requests` - HTTP requests to Google Street View API
- `python-dotenv` - Loading environment variables from .env file
- `pillow` - Image processing capabilities

### 2. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable the **Street View Static API**
4. Create an API key
5. Optionally restrict the API key to Street View Static API only

### 3. Configure API Key

Create a `.env` file in the project directory and add your API key:

```bash
# Create .env file
echo "google_maps_street_view_api=YOUR_ACTUAL_API_KEY" > .env
```

Or manually create a `.env` file with:

```
google_maps_street_view_api=YOUR_ACTUAL_API_KEY
```

Replace `YOUR_ACTUAL_API_KEY` with your actual Google Maps API key.

## Usage

### Quick Test (Recommended First)

```bash
python example_usage.py
# Choose option 1 for small test collection
```

This will collect images from just 3 locations to verify your setup works.

### Full Area Collection

```bash
python street_view_collector.py
```

Or use the example script:

```bash
python example_usage.py
# Choose option 2 for full collection
```

### Estimate Costs

```bash
python example_usage.py
# Choose option 3 to estimate API costs
```

## Collection Parameters

| Parameter          | Default Value          | Description                           |
| ------------------ | ---------------------- | ------------------------------------- |
| Center Coordinates | 34.865838, -120.447520 | Orcutt, California                    |
| Coverage Area      | 3.5 square miles       | Total area to survey                  |
| Grid Spacing       | 350 feet               | Distance between collection points    |
| Image Size         | 640x640 pixels         | Street view image dimensions          |
| Viewing Angles     | [0°, 90°, 180°, 270°]  | Four cardinal directions per location |
| Field of View      | 90 degrees             | Camera field of view                  |

## Output Structure

```
site_data/
├── raw_images/
│   ├── orcutt_0001_h000_20250709_143022.jpg
│   ├── orcutt_0001_h090_20250709_143023.jpg
│   ├── orcutt_0001_h180_20250709_143024.jpg
│   ├── orcutt_0001_h270_20250709_143025.jpg
│   └── ...
├── processed_images/
│   ├── train/
│   │   ├── diagonal_parking/
│   │   └── no_diagonal_parking/
│   ├── validation/
│   └── test/
└── metadata/
    └── collection_metadata_20250709_143020.csv
```

## Metadata

Each collection generates a CSV file with the following information:

- Filename and filepath
- GPS coordinates (latitude, longitude)
- Camera heading and field of view
- Timestamp
- File size
- Success/failure status
- Error messages (if any)

## Estimated Resource Usage

For the default 3.5 square mile area with 350-foot grid spacing:

- **Locations**: ~385 grid points
- **Total Images**: ~1,540 (4 per location)
- **API Requests**: ~1,540
- **Estimated Cost**: ~$10.78 (at $0.007 per request)
- **Storage**: ~154 MB (assuming ~100KB per image)
- **Collection Time**: ~4-6 minutes (with rate limiting)

## API Rate Limiting

The script includes a configurable delay between API calls (default 0.1 seconds) to respect Google's rate limits. For Google Maps APIs, the default limit is:

- 50 requests per second
- 25,000 requests per day

## Error Handling

The script handles common issues:

- Network timeouts and connection errors
- Invalid coordinates or API responses
- Rate limit exceeded (with automatic retry capability)
- Missing API key or invalid key
- File system errors

## Next Steps After Collection

1. **Review Images**: Manually inspect collected images for quality
2. **Data Labeling**: Begin labeling images for diagonal parking presence
3. **Data Preprocessing**: Resize, normalize, and augment images for training
4. **Model Training**: Use labeled data to train computer vision model

## Troubleshooting

### Common Issues

**API Key Error**:

```
ERROR: Please set your Google Maps API key
```

- Solution: Replace placeholder API key with your actual key

**Network Timeout**:

```
Failed to collect image: Connection timeout
```

- Solution: Check internet connection, increase timeout in script

**Quota Exceeded**:

```
API quota exceeded
```

- Solution: Check your Google Cloud Console quota limits

**No Images Collected**:

- Check API key permissions
- Verify Street View Static API is enabled
- Check coordinates are valid (not in ocean, restricted areas)

### Support

For issues with:

- **Google Maps API**: Check [Google Maps Platform documentation](https://developers.google.com/maps/documentation/streetview)
- **Script errors**: Review the generated log files and error messages
- **Rate limiting**: Increase delay_seconds parameter

## License

This code is part of the EV Charging Station Site Recommendation capstone project.

### Inspiration

https://www.youtube.com/watch?v=tHL5STNJKag&t=264s
