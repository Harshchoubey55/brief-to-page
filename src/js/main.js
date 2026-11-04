$(function () {
  var $header = $(".site-header");
  var $nav = $("#site-nav");
  var $toggle = $(".nav-toggle");

  // mobile menu
  $toggle.on("click", function () {
    var open = $nav.toggleClass("is-open").hasClass("is-open");
    $toggle.attr("aria-expanded", open);
  });
  $nav.on("click", "a", function () {
    $nav.removeClass("is-open");
    $toggle.attr("aria-expanded", false);
  });

  $(window).on("scroll", function () {
    $header.toggleClass("is-scrolled", window.scrollY > 10);
  });

  // FAQ: one answer open at a time
  $(".faq__q").on("click", function () {
    var $btn = $(this);
    var wasOpen = $btn.attr("aria-expanded") === "true";

    $(".faq__q").attr("aria-expanded", "false");
    $(".faq__a").attr("hidden", true);

    if (!wasOpen) {
      $btn.attr("aria-expanded", "true");
      $("#" + $btn.attr("aria-controls")).removeAttr("hidden");
    }
  });

  // download form - only checks input for now, nothing is sent anywhere
  var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  $("#download-form").on("submit", function (e) {
    e.preventDefault();
    var $form = $(this);
    var ok = true;

    $form.find("input[required]").each(function () {
      var $f = $(this);
      var val = $.trim($f.val());
      var bad = val === "" || ($f.attr("type") === "email" && !emailPattern.test(val));
      $f.toggleClass("is-invalid", bad).attr("aria-invalid", bad);
      if (bad) ok = false;
    });

    var $msg = $form.find(".form__msg");
    if (!ok) {
      $msg.text("Please fill in every field with a valid work email.");
      $form.find(".is-invalid").first().trigger("focus");
      return;
    }
    $msg.text("Thanks - the report is on its way to your inbox.");
    $form[0].reset();
  });
});
