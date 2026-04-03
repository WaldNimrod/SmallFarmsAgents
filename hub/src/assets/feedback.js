/**
 * Hub Feedback — generic client-side feedback export.
 * Parameterized: works for any Agents OS hub project.
 *
 * Usage (in HTML before </body>):
 *   <script src="assets/feedback.js"></script>
 *   <script>
 *     HubFeedback.init({
 *       exportType: "sfa-feedback",
 *       defaultRespondent: "Nimrod",
 *       decisionIds: ["D-01", "D-02", "D-03"]
 *     });
 *   </script>
 */
(function () {
  "use strict";
  var SCHEMA_VERSION = 1;

  function $(id) {
    return document.getElementById(id);
  }

  function buildPayload(config) {
    var answers = [];
    (config.decisionIds || []).forEach(function (did) {
      var choiceEl = $("choice-" + did);
      var notesEl = $("notes-" + did);
      var choice = choiceEl ? choiceEl.value.trim() : "";
      var notes = notesEl ? notesEl.value.trim() : "";
      if (choice || notes) {
        answers.push({ id: did, choice: choice, notes: notes });
      }
    });
    return {
      schemaVersion: SCHEMA_VERSION,
      exportType: config.exportType || "hub-feedback",
      exportTimestamp: new Date().toISOString(),
      respondent:
        ($("respondent") && $("respondent").value.trim()) ||
        config.defaultRespondent ||
        "",
      answers: answers,
    };
  }

  function safeTimestamp() {
    return new Date()
      .toISOString()
      .replace(/\.\d{3}Z$/, "Z")
      .replace(/:/g, "-");
  }

  function downloadJson(obj, prefix) {
    var blob = new Blob([JSON.stringify(obj, null, 2)], {
      type: "application/json;charset=utf-8",
    });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = (prefix || "hub-feedback") + "-" + safeTimestamp() + ".json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(a.href);
  }

  window.HubFeedback = {
    init: function (config) {
      config = config || {};
      var btn = $("btn-export-json");
      if (!btn) return;
      btn.addEventListener("click", function () {
        var payload = buildPayload(config);
        if (!payload.answers.length) {
          alert("\u05d0\u05d9\u05df \u05ea\u05e9\u05d5\u05d1\u05d5\u05ea \u05dc\u05d9\u05d9\u05e6\u05d5\u05d0");
          return;
        }
        downloadJson(payload, config.exportType || "hub-feedback");
      });
    },
  };
})();
