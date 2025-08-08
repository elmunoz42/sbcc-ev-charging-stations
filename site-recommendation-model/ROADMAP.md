# ROADMAP For EV Charging Station Location Classification Using Street View Images

## Project Overview

Develop a computer vision model to automatically identify optimal EV charging station locations by classifying street view images for diagonal parking availability - a key infrastructure criterion for accessible charging stations.

## ✅ Completed: Phase 1 & 2 - Data Collection & Initial Model Training

### Data Collection

- ✅ Google Street View Static API integration
- ✅ Geographic grid generation around Orcutt, CA
- ✅ Multi-angle image collection (0°, 90°, 180°, 270°)
- ✅ Metadata tracking and organization
- ✅ Cost optimization (reduced to 3.5 sq miles)

### Initial Model Development

- ✅ MobileNetV2 transfer learning implementation
- ✅ CPU-optimized training pipeline
- ✅ Data augmentation for small dataset
- ✅ Model checkpointing and early stopping
- ✅ Achieved 97.2% validation accuracy

## 🔄 Current: Phase 3 - Model Improvement & Evaluation

### Model Performance Assessment

- ✅ Test set evaluation
- ✅ Identification of class imbalance issue (25:1 ratio)
- ✅ Error analysis on misclassified images
- ⏳ Integration with existing EV infrastructure analysis

### Data Enhancement

- 🔍 Collect 100-200 more diagonal parking examples
  - Target: Improve from 25:1 to 3:1 ratio (no_diagonal:diagonal)
- 🔍 Review and verify existing 14 diagonal parking labels
- 🔍 Develop systematic labeling workflow for new images

## 🔜 Upcoming: Phase 4 - Advanced Model Optimization

### Training Refinements

- Implement class weights to address severe imbalance
- Enhanced data augmentation specifically for minority class
- Explore additional architectures (ResNet, EfficientNet)
- Hyperparameter optimization
  - Learning rate scheduling
  - Dropout tuning
  - Regularization techniques

### Technical Improvements

- Address CUDA/GPU compatibility for faster training
- Implement TensorFlow mixed precision for efficiency
- Optimize batch processing for large-scale inference
- Model quantization for deployment efficiency

## 🎯 Future: Phase 5 - Production Integration

### Site Recommendation System

- Batch processing of all collected street view images
- Development of composite scoring algorithm
  - Diagonal parking presence
  - Proximity to amenities
  - Traffic patterns
  - Electrical infrastructure
- Geographic visualization of optimal locations
- Integration with county planning systems

### Validation & Deployment

- Field validation of top-ranked sites
- Deployment of model as standalone service
- API development for integration with GIS systems
- Documentation and training for county staff

## Success Metrics

### Technical Metrics

- **Model Performance**:
  - Current: 97.2% validation accuracy but with class bias
  - Target: >90% balanced accuracy across classes
- **Precision/Recall**: >85% for diagonal parking class
- **Processing Speed**: <1 second per image on CPU

### Business Impact

- **Coverage**: Evaluate all 1,540 collected images
- **Value Delivery**: Identify at least 10 viable new charging locations
- **ROI**: Reduce site selection costs by >50% compared to manual methods

## Next Steps (August 2025)

1. **Immediate (Week 1):**

   - Collect and label 50+ additional diagonal parking examples
   - Implement class weights in training script
   - Re-train model with balanced approach

2. **Short-term (Weeks 2-3):**

   - Process entire image collection for site recommendations
   - Develop scoring system for ranking potential sites
   - Create visualization of top recommended locations

3. **Medium-term (Weeks 4-6):**
   - Field validation of top-ranked sites
   - Refine model based on validation findings
   - Document complete methodology for stakeholders

This refined roadmap reflects our current progress and prioritizes addressing the class imbalance issue while moving toward practical site recommendations for Santa Barbara County.

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
