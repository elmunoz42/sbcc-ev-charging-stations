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

## Machine Learning Model

### Current Status ✅

The diagonal parking classifier has been successfully trained and is ready for use!

- **Model Architecture**: MobileNetV2 transfer learning with binary classification
- **Training Data**: 367 labeled images (14 diagonal parking, 353 no diagonal parking)
- **Model Performance**: 97.2% validation accuracy during training
- **Saved Model**: `site_data/model_checkpoints/best_model.h5`

### Using the Trained Model

**Single Image Prediction**:

```bash
python predict_cpu.py --model site_data/model_checkpoints/best_model.h5 --image path/to/image.jpg
```

**Batch Processing**:

```bash
python predict_cpu.py --model site_data/model_checkpoints/best_model.h5 --batch path/to/images/ --output results.csv
```

**Training Your Own Model**:

```bash
# CPU training (recommended for most setups)
python train_model_cpu.py

# GPU training (if CUDA is properly configured)
python diagonal_parking_classifier.py
```

### Model Files

- `diagonal_parking_classifier.py` - Core ML model implementation
- `train_model_cpu.py` - CPU-optimized training script
- `predict_cpu.py` - Prediction script for inference
- `quick_eval.py` - Quick evaluation on test images

### Current Model Limitations

The current model has a significant class imbalance issue that affects its predictions:

- **Training Distribution**: 14 diagonal parking vs. 353 no_diagonal_parking images (25:1 ratio)
- **Impact**: Model is biased toward predicting the majority class (no_diagonal_parking)
- **Test Results**: Current model achieves 97.2% overall accuracy but has poor recall for diagonal parking class
- **Class Mapping**: diagonal_parking=0, no_diagonal_parking=1 (important for interpreting model outputs)

This is why the "Next Steps" section emphasizes collecting more diagonal parking examples and implementing class weights. Despite this limitation, the model architecture is sound and can achieve excellent results once the data imbalance is addressed.

## Next Steps for Improvement

### Phase 1: Data Collection & Labeling 🎯

1. **Expand Diagonal Parking Dataset**: Collect 100-200 more diagonal parking examples
   - Current imbalance: 25:1 ratio (no_diagonal:diagonal)
   - Target: 3:1 or better ratio for improved model performance
2. **Review Current Labels**: Manually verify existing 14 diagonal parking labels
3. **Systematic Labeling**: Use Google Sheets integration for collaborative labeling

### Phase 2: Model Optimization 🔧

1. **Class Weight Balancing**: Implement class weights to handle data imbalance
   ```python
   # Example implementation in train_model_cpu.py
   class_weights = {
       0: 25.0,  # diagonal_parking (increase weight for minority class)
       1: 1.0    # no_diagonal_parking
   }
   model.compile(..., loss=tf.keras.losses.BinaryCrossentropy(class_weight=class_weights))
   ```
2. **Advanced Data Augmentation**: Increase augmentation for minority class
   - Implement more aggressive rotation, zoom, and brightness variations
   - Consider synthetic data generation for diagonal parking class
3. **Model Architecture**: Experiment with other pre-trained models (ResNet, EfficientNet)
4. **Hyperparameter Tuning**: Optimize learning rates, batch sizes, and regularization

### Phase 3: Production Deployment 🚀

1. **Batch Processing**: Apply model to all collected street view images
   ```bash
   # Process all images in the raw_images directory
   python predict_cpu.py --model site_data/model_checkpoints/best_model.h5 --batch site_data/raw_images/ --output site_recommendations.csv
   ```
2. **Site Scoring**: Develop composite scoring system for EV charging site recommendations
   - Combine diagonal parking detection with other criteria (amenities, traffic, etc.)
   - Create weighted scoring algorithm for ranking potential sites
3. **Validation**: Field validation of top-ranked sites
4. **Integration**: Connect with existing EV infrastructure analysis in Santa Barbara County

### Quick Wins (August 2025)

- ✅ Create labeled dataset balancer script to match class distributions
- ✅ Update training script with class weights
- ✅ Generate batch recommendations for top 10 sites in Orcutt area

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
