// app.js (hoặc trong thẻ <script> của HTML)

// ... các hàm getRiskLevel, getActiveSymptoms, displayResult ...

const SVM_API_URL = "http://127.0.0.1:5000/predict_stroke_risk"; // Đảm bảo URL này đúng

// Xử lý form submit
document
  .getElementById("diagnosisForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    // Hiển thị loading spinner và ẩn kết quả cũ
    document.getElementById("loadingSpinner").style.display = "block";
    document.getElementById("resultContainer").classList.add("hidden");
    document.getElementById("aiAdvice").innerHTML = "Đang tạo lời khuyên..."; // Reset advice text
    document.getElementById("chatMessages").innerHTML = ""; // Clear chat history

    // Thu thập dữ liệu form
    const formData = {
      chest_pain: parseInt(document.getElementById("chest_pain").value),
      shortness_of_breath: parseInt(
        document.getElementById("shortness_of_breath").value
      ),
      irregular_heartbeat: parseInt(
        document.getElementById("irregular_heartbeat").value
      ),
      fatigue_weakness: parseInt(
        document.getElementById("fatigue_weakness").value
      ),
      dizziness: parseInt(document.getElementById("dizziness").value),
      swelling: parseInt(document.getElementById("swelling").value),
      pain_in_neck: parseInt(document.getElementById("pain_in_neck").value),
      excessive_sweating: parseInt(
        document.getElementById("excessive_sweating").value
      ),
      persistent_cough: parseInt(
        document.getElementById("persistent_cough").value
      ),
      nausea: parseInt(document.getElementById("nausea").value),
      high_blood_pressure: parseInt(
        document.getElementById("high_blood_pressure").value
      ),
      chest_discomfort: parseInt(
        document.getElementById("chest_discomfort").value
      ),
      cold_hand: parseInt(document.getElementById("cold_hand").value),
      snoring: parseInt(document.getElementById("snoring").value),
      anxiety: parseInt(document.getElementById("anxiety").value),
      age: parseInt(document.getElementById("age").value),
    };

    // Kiểm tra tuổi đã nhập chưa và có hợp lệ không
    if (isNaN(formData.age) || formData.age < 1 || formData.age > 120) {
      alert("Vui lòng nhập tuổi hợp lệ (từ 1 đến 120)!");
      document.getElementById("loadingSpinner").style.display = "none";
      return;
    }

    try {
      // --- ĐÂY LÀ PHẦN QUAN TRỌNG NHẤT: GỬI DỮ LIỆU ĐẾN API BACKEND SVM ---
      const response = await fetch(SVM_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData), // Gửi trực tiếp formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          `Lỗi từ API SVM: ${errorData.error || response.statusText}`
        );
      }

      const svmResult = await response.json();

      // Tạo đối tượng riskData từ kết quả SVM và các triệu chứng đã chọn
      const riskData = {
        percentage: svmResult.percentage,
        level: svmResult.level,
        symptoms: getActiveSymptoms(formData), // Lấy triệu chứng từ formData gốc
        age: formData.age,
      };

      currentRiskData = riskData; // Lưu dữ liệu nguy cơ cho phần chat AI

      // Hiển thị kết quả cơ bản
      displayResult(riskData);

      // Ẩn loading và lấy lời khuyên AI sau khi hiển thị kết quả cơ bản
      document.getElementById("loadingSpinner").style.display = "none";
      await getGeminiAdvice(riskData); // Gọi Gemini API để lấy lời khuyên
    } catch (error) {
      console.error("Lỗi khi gọi API SVM:", error);
      document.getElementById("loadingSpinner").style.display = "none";
      alert(
        `Đã xảy ra lỗi khi dự đoán nguy cơ: ${error.message}\nVui lòng đảm bảo backend SVM đang chạy.`
      );
      // Fallback về demo nếu API SVM không hoạt động
      const demoRiskData = {
        percentage: 50, // Giá trị demo
        level: "medium", // Giá trị demo
        symptoms: getActiveSymptoms(formData),
        age: formData.age,
      };
      displayResult(demoRiskData);
      getGeminiAdvice(demoRiskData); // Dùng demo data cho Gemini
    }
  });

// ... các hàm khác như sendChat, getDemoChatResponse, v.v.
