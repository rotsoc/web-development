//////////////////////////////////////////////////////////////////////////////////////////////////
// Utilities

// Printing to the console
function print(what) {
	console.log(what)
}

// Plural correctiveness
function star_or_stars(amount) {
	if (amount > 1 || amount === 0) {
		return amount + " Stars";
	}
	else if (amount === 1) {
		return amount + " Star";
	}
	else {
		return "";
	}
}

function deactivate_button(button) {
	$(button).attr("aria-pressed", "false");
	$(button).removeClass("active");
}

//////////////////////////////////////////////////////////////////////////////////////////////////
// Parameters

var current_index = undefined;

var zero_stars = false;
var saved_rating = undefined;

var rating_value = $("#rating-value");
var rating_value_label = $("#rating-value-label");

$(function () {
	var popover_content = "<i class='fas fa-exclamation-circle'></i> You need to rate the book.";

	$("#rater-widget").popover({
		trigger: "manual",
		placement: "top",
		content: popover_content,
		html: true
	});
})

function checkRater() {
	if (rating_value.attr("value") !== undefined) {
		$("#rater-widget").popover("hide");
	}
	else {
		$("#rater-widget").popover("show");
	}
}

function toggle_zero_stars() {
	if (zero_stars) {
		if (saved_rating !== undefined) {
			starsRating.setRating(saved_rating);
			rating_value.attr("value", saved_rating);
			rating_value_label.text(star_or_stars(saved_rating));
		}
		else {
			starsRating.setRating(undefined);
			rating_value.removeAttr("value");
			rating_value_label.text("");
		}

		zero_stars = false;
	}
	else {
		if (saved_rating !== undefined) {
			starsRating.setRating(0);
			rating_value.attr("value", 0);
			rating_value_label.text(star_or_stars(0));
		}
		else {
			starsRating.setRating(0);
			rating_value.attr("value", 0);
			rating_value_label.text(star_or_stars(0));
		}

		zero_stars = true;
	}
	checkRater();
}

var starsRating = raterJs({
	starSize: 28,
	showToolTip: false,

	// When Clicked
	element: document.querySelector("#rater-widget"),
	rateCallback:function rateCallback(rating, done) {
		if (rating !== 0) {
			if (zero_stars) {
				rating_value_label.text(star_or_stars(rating));
				deactivate_button(".zero-button");
				zero_stars = false;
			}

			this.setRating(rating);
			rating_value.attr("value", rating);
			saved_rating = rating;
			checkRater();
		}

		done();
	},
	onHover: function(currentIndex, currentRating) {
		if (currentIndex !== 0) {
			rating_value_label.text(star_or_stars(currentIndex));
		}

		else {
			if (zero_stars) {
				rating_value_label.text(star_or_stars(currentRating));
			}

			else {
				rating_value_label.text("");
			}
		}
	},
	onLeave: function(currentIndex, currentRating) {
		if (zero_stars) {
			rating_value_label.text(star_or_stars(0));
		}

		else {
			if (currentRating === undefined) {
				rating_value_label.text(star_or_stars(""));
			}
			else {
				rating_value_label.text(star_or_stars(currentRating));
			}
		}
	}
});

window.addEventListener("load", starsRating, false);