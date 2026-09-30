(function () {
  var mapEl = document.getElementById("map");
  if (!mapEl || typeof L === "undefined") {
    return;
  }

  var markers = [];
  try {
    markers = JSON.parse(mapEl.getAttribute("data-markers") || "[]");
  } catch (e) {
    return;
  }
  if (!markers.length) {
    return;
  }

  var map = L.map(mapEl).setView([markers[0].lat, markers[0].lng], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap",
  }).addTo(map);

  var bounds = [];
  markers.forEach(function (m) {
    var marker = L.marker([m.lat, m.lng]).addTo(map);
    var label = m.name || "Provider";
    if (m.url) {
      marker.bindPopup('<a href="' + m.url + '">' + label + "</a>");
    } else {
      marker.bindPopup(label);
    }
    bounds.push([m.lat, m.lng]);
  });

  if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [24, 24] });
  }
})();
