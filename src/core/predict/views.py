from rest_framework.generics import CreateAPIView
from rest_framework import status
from core.utils.response import response_with_detail
from rest_framework.permissions import IsAuthenticated
from .serializers import PredictSerializer
from core.settings.common import BASE_DIR
import numpy as np
import tensorflow as tf
import pickle as pk


class PredictView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PredictSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transformed_data = self._transform_keys(serializer.validated_data)

        cnn_model_1d = tf.keras.models.load_model(BASE_DIR / "static/model/cnn_model_1d.h5")
        pca = pk.load(open(BASE_DIR / "static/model/pca_data.pkl", "rb"))
        scaler = pk.load(open(BASE_DIR / "static/model/scaler.pkl", "rb"))

        features_matrix = np.array(list(transformed_data.values())).reshape(1, -1)

        features_pca = pca.transform(features_matrix)
        features_scaled = scaler.transform(features_pca)
        features_scaled_reshaped = features_scaled.reshape(-1, 2, 1)

        predictions = cnn_model_1d.predict(features_scaled_reshaped)
        predicted_class = np.argmax(predictions)

        # Convert predictions to a list and round to 4 decimals
        predictions_list = [round(float(pred), 4) for pred in predictions[0]]

        # Return the predictions and the predicted class in the response
        return response_with_detail(
            status_code=status.HTTP_201_CREATED,
            predictions={
                "benign": predictions_list[0],
                "ransomware": predictions_list[1],
                "spyware": predictions_list[2],
                "trojan": predictions_list[3],
            },
            predicted_class=predicted_class,
        )

    @staticmethod
    def _transform_keys(data):
        transformed = {}
        for key, value in data.items():
            transformed_key = key.replace("_", ".", 1)
            transformed[transformed_key] = value
        return transformed
