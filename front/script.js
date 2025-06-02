function toggleMedicineInput() {
  const inputArea = document.getElementById("medicine-input-area");
  inputArea.classList.toggle("hidden");
}

function checkMedicine() {
  const name = document.getElementById("medicineInput").value.trim();
  const output = document.getElementById("medicine-response");
  if (name) {
    output.innerHTML = `💡 모델 응답: <strong>${name}</strong>은(는) 복용 시 충분한 수분 섭취와 휴식이 권장됩니다.\n필요시 병원 방문을 고려하세요.`;
  } else {
    output.innerHTML = "💡 입력한 약에 대한 대처법이 여기에 표시됩니다.";
  }
}