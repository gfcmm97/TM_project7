let 정제된증상 = "";
let 추천약리스트 = [];

async function fetchHospitalRecommendations() {
  const symptomInput = document.getElementById("symptomInput").value.trim();
  if (!symptomInput) return;

  // 로딩 표시
  document.getElementById("loading").classList.remove("hidden");

  try {
    const response = await fetch("http://localhost:8000/recommend/hospitals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symptom: symptomInput })
    });

    const data = await response.json();
    console.log("[병원 추천 응답]", data);

    if (!data["정제된_증상"] || !Array.isArray(data["추천_질병"]) || data["추천_질병"].length === 0) {
      document.getElementById("hospital-list").innerHTML = `<div></div><div class="warning-message">⚠️ 관련된 정보를 찾을 수 없습니다. 증상을 다시 입력해 주세요.</div><div></div>`;
      document.getElementById("loading").classList.add("hidden");
      return;
    }

    정제된증상 = data["정제된_증상"];
    document.getElementById("department").innerText =
      Array.isArray(data["추천_진료과"]) && data["추천_진료과"].length > 0
        ? data["추천_진료과"].join(", ")
        : "-";
    
    const diseaseList = data["추천_질병"] || [];
    document.getElementById("disease").innerText = diseaseList.length > 0 ? diseaseList.join(", ") : "-";

    const 병원HTML = data["추천_병원"]
      .map(h => {
        const mapURL = `https://map.kakao.com/link/to/${h["병원명"]},37.0,127.0`;
        return `
        <a href="${mapURL}" target="_blank" rel="noopener noreferrer" class="hospital-link">
          <div class="hospital-card">
            <strong>${h["병원명"]}</strong><br />
            ${h["주소"]}
            <div class="reviews">
            <span>${h["키워드_요약"] ? "👍 " + h["키워드_요약"] : "👎 리뷰 정보 없음"}</span>
            </div>
          </div>
        </a>
        `;
      }).join("");

    // 추천 약 렌더링
    const 약HTML = Array.isArray(data["추천_약"]) && data["추천_약"].length > 0
      ? data["추천_약"].map(m => `
        <li>
          <strong>${m["itemName"]}</strong> (${m["entpName"]})<br />
          💊 효능: ${m["efcyQesitm"] || "정보 없음"}<br />
          🚫 함께 복용 주의: ${m["intrcQesitm"] || "정보 없음"}
        </li>
      `).join("")
      : "<li>추천 약 없음</li>";

    document.getElementById("medicine-list").innerHTML = 약HTML;
    추천약리스트 = data["추천_약"] || [];

    document.getElementById("hospital-list").innerHTML = 병원HTML;
  } catch (err) {
    console.error("API 호출 실패", err);
  } finally {
    // 로딩 숨기기
    document.getElementById("loading").classList.add("hidden");
  }
}

// 버튼 클릭 이벤트
document.getElementById("submitBtn").addEventListener("click", fetchHospitalRecommendations);

// Enter 키 이벤트
document.getElementById("symptomInput").addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault(); // 줄바꿈 방지
    fetchHospitalRecommendations();
  }
});

document.getElementById("medicineInput").addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    checkMedicine();
  }
});

async function checkMedicine() {
  const userInput = document.getElementById("medicineInput").value.trim();
  const output = document.getElementById("medicine-response");

  document.getElementById("medicine-loading").classList.remove("hidden");

  if (!userInput || 추천약리스트.length === 0) {
    output.innerHTML = "⚠️ 상비약 또는 추천 약 정보가 없습니다.";

    document.getElementById("medicine-loading").classList.add("hidden");
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/recommend/medicine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        symptom_keywords: 정제된증상.split(",").map(s => s.trim()),
        user_medicine: userInput,
        top_k: 10,
        risk_threshold: 0.6
      })
    });

    const 약들 = await response.json();

    // 위험 약: 유사도 있는 경우만 (0.8 이상)
    const 위험약 = 약들.filter(m => m.interaction_score !== undefined && m.interaction_score >= 0.8);

    if (위험약.length === 0) {
      output.innerHTML = "✅ 함께 복용해도 괜찮습니다.";
    } else {
      const 위험HTML = 위험약.slice(0, 3).map(med => `
        <div class="dangerous-medicine">
          ⚠️ <strong>${med.itemName}</strong><br/>
          📌 효능: ${med.efcyQesitm || "정보 없음"}<br/>
          ❗ 유사도: ${Number(med.interaction_score).toFixed(3)}
        </div>
      `).join("");

      output.innerHTML = `
        <b>🚫 보유하신 "${userInput}"과 함께 복용하면 위험한 약은 다음과 같습니다:</b><br/>
        ${위험HTML}
      `;
    }
  } catch (err) {
    console.error("상비약 검사 실패", err);
    output.innerHTML = "❌ 오류 발생: 상비약 위험 여부를 불러오지 못했습니다.";
  } finally {

    document.getElementById("medicine-loading").classList.add("hidden");
  }
}

function toggleMedicineInput() {
  const inputArea = document.getElementById("medicine-input-area");
  inputArea.classList.toggle("hidden");
}
