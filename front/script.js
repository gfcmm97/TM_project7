let 정제된증상 = "";

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
