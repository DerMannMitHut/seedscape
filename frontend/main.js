async function loadHex(campaign, id) {
  const res = await fetch(`/api/${campaign}/hex/${id}`);
  const data = await res.json();
  document.getElementById("info").innerText = JSON.stringify(data, null, 2);
}

loadHex("default", "A1");
