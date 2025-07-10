# ROADMAP For EV Charging Station Location Classification Using Street View Images

## Project Overview

Develop a computer vision model to automatically identify optimal EV charging station locations by classifying street view images for diagonal parking availability - a key infrastructure criterion for accessible charging stations.

## Phase 1: Data Collection & Preparation (Weeks 1-2)

### 1.1 Street View Image Extraction

- **Google Street View Static API Setup**
  - Obtain API key and set up billing
  - Define target geographic areas (Santa Barbara County focus)
  - Create coordinate grid for systematic sampling
- **Image Collection Strategy**
  - Extract 640x640 pixel square images
  - Collect multiple angles per location (0°, 90°, 180°, 270°)
  - Target 1000-2000 initial images across diverse locations
  - Include urban, suburban, and rural areas

### 1.2 Data Organization

```python
site_data/
├── raw_images/
│   ├── location_id_angle_timestamp.jpg
├── processed_images/
│   ├── train/
│   │   ├── diagonal_parking/
│   │   └── no_diagonal_parking/
│   ├── validation/
│   └── test/
└── metadata/
    └── image_labels.csv
```

## Phase 2: Data Labeling & Preprocessing (Week 2-3)

### 2.1 Manual Labeling Protocol

- **Binary Classification**: Diagonal parking present/absent
- **Labeling Criteria**:
  - Clear diagonal parking spaces visible
  - Adequate space for charging equipment installation
  - Safe pedestrian access
  - Minimum 3-4 diagonal spaces in view

### 2.2 Data Preprocessing Pipeline

```python
# Image preprocessing steps
- Resize to 224x224 (ImageNet standard)
- Normalize pixel values (ImageNet mean/std)
- Data augmentation (rotation, brightness, contrast)
- Train/validation/test split (70/15/15)
```

## Phase 3: Model Development (Weeks 3-4)

### 3.1 Transfer Learning Setup

- **Base Model**: Use pre-trained ResNet50 or EfficientNet from ImageNet
- **Architecture Modifications**:
  - Freeze early convolutional layers
  - Replace final classification layer
  - Add dropout layers for regularization

### 3.2 PyTorch Implementation

```python
# Key components to implement
- Custom Dataset class for street view images
- Data loaders with augmentation
- Transfer learning model setup
- Training loop with validation
- Model checkpointing and early stopping
```

### 3.3 Training Strategy

- **Loss Function**: Binary Cross Entropy
- **Optimizer**: Adam with learning rate scheduling
- **Metrics**: Accuracy, Precision, Recall, F1-Score
- **Validation**: Stratified sampling to ensure class balance

## Phase 4: Model Training & Optimization (Week 4-5)

### 4.1 Initial Training

- Start with small learning rate (1e-4)
- Train for 20-30 epochs initially
- Monitor overfitting with validation metrics
- Use GPU acceleration on Colab Pro

### 4.2 Hyperparameter Tuning

- Learning rate scheduling
- Batch size optimization
- Dropout rate adjustment
- Data augmentation parameters

### 4.3 Model Evaluation

- Confusion matrix analysis
- ROC curve and AUC calculation
- Error analysis on misclassified images
- Geographic bias assessment

## Phase 5: Integration & Deployment (Week 5-6)

### 5.1 Batch Prediction Pipeline

```python
# Pipeline for processing new locations
def evaluate_location(lat, lon):
    images = extract_street_view_images(lat, lon)
    processed_images = preprocess_batch(images)
    predictions = model.predict(processed_images)
    confidence_score = aggregate_predictions(predictions)
    return confidence_score
```

### 5.2 Geographic Integration

- Create grid-based evaluation system
- Generate probability maps for Santa Barbara County
- Integrate with existing GIS data (zoning, traffic, demographics)
- Output ranked list of potential charging locations

## Phase 6: Validation & Documentation (Week 6)

### 6.1 Field Validation

- Ground truth verification for top-ranked locations
- Compare with existing charging station placements
- Validate against Santa Barbara County's current EV infrastructure

### 6.2 Capstone Integration

- **Technical Documentation**: Jupyter notebook with full pipeline
- **Non-Technical Report**: Business impact and implementation recommendations
- **Model Deployment**: Containerized prediction service for County use

## Technical Requirements & Tools

### Google Colab Setup

```python
# Essential libraries
!pip install torch torchvision
!pip install pillow requests pandas numpy matplotlib
!pip install googlemaps folium geopandas
!pip install scikit-learn seaborn

# GPU verification
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

### Data Storage Strategy

- Use Google Drive for dataset storage (within Colab Pro limits)
- Implement efficient data loading with PyTorch DataLoader
- Consider image compression for storage optimization

## Success Metrics

### Technical Metrics

- **Model Performance**: >85% accuracy on test set
- **Precision**: >80% (minimize false positives)
- **Recall**: >75% (capture most viable locations)
- **Processing Speed**: <1 second per location evaluation

### Business Impact Metrics

- **Coverage**: Evaluate 100+ potential locations in Santa Barbara County
- **Validation**: 90% agreement with expert manual assessment
- **Integration**: Seamless incorporation into County's EV planning workflow

## Risk Mitigation

### Technical Risks

- **Limited training data**: Implement active learning for efficient labeling
- **Geographic bias**: Ensure diverse sampling across county regions
- **Weather/lighting variation**: Include temporal diversity in dataset

### Project Risks

- **API costs**: Monitor Google Street View API usage
- **Timeline pressure**: Focus on minimum viable product first
- **Scope creep**: Maintain focus on diagonal parking classification

## Next Steps

1. Set up Google Street View API and test image extraction
2. Create initial dataset with 200-300 labeled images
3. Implement basic PyTorch training pipeline
4. Iterate on model architecture and training parameters
5. Scale up data collection based on initial results

This approach aligns with your capstone requirements while providing a practical tool for Santa Barbara County's EV infrastructure planning efforts.
