


# Later, to load the model:
with open('stlf_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

# Use the loaded model to make forecasts
forecast30 = loaded_model.forecast(len(y_test))