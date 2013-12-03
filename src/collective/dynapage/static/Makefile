all: dynacarousel.js dynapage.css

dynacarousel.js: dynacarousel.coffee
	coffee -c dynacarousel.coffee

dynapage.css: dynapage.scss
	scss -t expanded dynapage.scss dynapage.css

