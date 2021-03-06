window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

jQuery(($) => {
  $(document).on("click", ".venue-show .btn-delete", async function () {
    const el = $(this);
    try {
      if (!confirm("Delete " + el.data("name") + ".\nAre you sure?")) return;
      const res = await fetch("/venues/" + el.data("id"), { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      window.location = "/venues";
    } catch (error) {
      alert(error.message || "Failed to delete");
    }
  });
});
