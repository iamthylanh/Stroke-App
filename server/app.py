# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
# import pandas as pd # Không cần thiết nếu bạn không dùng DataFrame ở đây

app = Flask(__name__)
CORS(app)

# Đường dẫn đến file model và scaler đã lưu
MODEL_PATH = 'model_and_scaler.pkl'

# Tải mô hình và scaler khi ứng dụng khởi động
try:
    with open(MODEL_PATH, 'rb') as f:
        loaded_assets = pickle.load(f)
        model = loaded_assets['model']
        scaler = loaded_assets['scaler']
    print(f"✅ Đã tải mô hình và scaler từ '{MODEL_PATH}' thành công.")
except FileNotFoundError:
    print(f"❌ Lỗi: Không tìm thấy file '{MODEL_PATH}'. Đảm bảo file nằm cùng thư mục với app.py.")
    model = None
    scaler = None
except Exception as e:
    print(f"❌ Lỗi khi tải mô hình/scaler: {e}")
    model = None
    scaler = None

# Định nghĩa thứ tự các feature (đúng như X_names trong code train của bạn)
# Đây là thứ tự mà mô hình SVM mong đợi dữ liệu đầu vào
FEATURE_ORDER = [
    "Chest Pain", "Shortness of Breath", "Irregular Heartbeat", "Fatigue & Weakness",
    "Dizziness", "Swelling (Edema)", "Pain in Neck/Jaw/Shoulder/Back", "Excessive Sweating",
    "Persistent Cough", "Nausea/Vomiting", "High Blood Pressure", "Chest Discomfort (Activity)",
    "Cold Hands/Feet", "Snoring/Sleep Apnea", "Anxiety/Feeling of Doom", "Age"
]

@app.route('/predict_stroke_risk', methods=['POST'])
def predict_stroke_risk():
    if model is None or scaler is None:
        print("DEBUG: Mô hình hoặc Scaler chưa được tải.") # Debugging print
        return jsonify({"error": "Mô hình hoặc Scaler chưa được tải. Vui lòng kiểm tra file model_and_scaler.pkl."}), 500

    data = request.get_json(force=True) # Lấy dữ liệu JSON từ request
    print(f"DEBUG: Dữ liệu nhận được từ frontend: {data}") # Debugging print

    # Kiểm tra xem tất cả các trường cần thiết có trong dữ liệu không
    # Các tên trường trong JSON phải khớp với tên id trong form HTML của bạn
    required_fields = [
        'chest_pain', 'shortness_of_breath', 'irregular_heartbeat', 'fatigue_weakness',
        'dizziness', 'swelling', 'pain_in_neck', 'excessive_sweating',
        'persistent_cough', 'nausea', 'high_blood_pressure', 'chest_discomfort',
        'cold_hand', 'snoring', 'anxiety', 'age'
    ]

    for field in required_fields:
        if field not in data:
            print(f"DEBUG: Thiếu trường: {field}") # Debugging print
            return jsonify({"error": f"Thiếu dữ liệu cho trường: {field}"}), 400

    try:
        # Chuyển đổi dữ liệu JSON thành một list theo đúng thứ tự FEATURE_ORDER
        # Các tên trong data[] phải khớp với các id trong HTML form của bạn
        input_features = [
            data['chest_pain'],
            data['shortness_of_breath'],
            data['irregular_heartbeat'],
            data['fatigue_weakness'],
            data['dizziness'],
            data['swelling'],
            data['pain_in_neck'],
            data['excessive_sweating'],
            data['persistent_cough'],
            data['nausea'],
            data['high_blood_pressure'],
            data['chest_discomfort'],
            data['cold_hand'],
            data['snoring'],
            data['anxiety'],
            data['age']
        ]
        print(f"DEBUG: input_features (trước scale): {input_features}") # Debugging print

        # Chuyển đổi list thành numpy array và reshape cho scaler (1 sample, n features)
        input_array = np.array(input_features).reshape(1, -1)

        # Áp dụng scaler đã huấn luyện
        scaled_input = scaler.transform(input_array)
        print(f"DEBUG: scaled_input (sau scale): {scaled_input}") # Debugging print

        # Dự đoán xác suất
        # predict_proba trả về mảng 2D: [[prob_class_0, prob_class_1]]
        # Chúng ta muốn xác suất của class 1 (bị bệnh)
        probability_at_risk = model.predict_proba(scaled_input)[0, 1]
        print(f"DEBUG: Raw probability (trước làm tròn): {probability_at_risk}") # Debugging print
        risk_percentage = round(probability_at_risk * 100)
        print(f"DEBUG: risk_percentage (sau làm tròn): {risk_percentage}") # Debugging print


        # Xác định mức độ rủi ro (giống như logic hiện tại của bạn)
        def get_risk_level(percentage):
            if percentage < 25: return 'low'
            if percentage < 60: return 'medium'
            return 'high'

        risk_level = get_risk_level(risk_percentage)

        return jsonify({
            "percentage": risk_percentage,
            "level": risk_level,
            "message": "Dự đoán thành công"
        })

    except Exception as e:
        print(f"DEBUG: Lỗi xảy ra trong try block: {str(e)}") # Debugging print
        return jsonify({"error": f"Lỗi trong quá trình dự đoán: {str(e)}"}), 500

if __name__ == '__main__':
    # Chạy ứng dụng Flask trên cổng 5000
    # Trong môi trường production, bạn sẽ dùng Gunicorn hoặc uWSGI
    app.run(debug=True, port=5000)