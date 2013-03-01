\version "2.16.0"

#(set-global-staff-size 16)

%\include "../reduce-whitespace.ly"
%\include "articulate.ly"
\paper{
  indent=10\mm
  paper-width = 250\mm
}
 
\header {
  arranger = "arr. Graham Percival"
title = "Eine kleine Nachtmusik"
subtitle = "Movement 1"
composer = "Wolfgang Amadeus Mozart (1756 - 1791)"
%opus = "K. 525"
piece = "Allegro"
mutopiatitle = "Eine kleine Nachtmusik (1st movement)"
mutopiacomposer = "MozartWA"
mutopiaopus = "KV 525"
mutopiainstrument = "Violin, Viola, Cello, Double Bass"
date = "1787"
source = "http://www.imslp.org/"
style = "Classical"
copyright = "Public Domain"
maintainer = "Anonymous"
maintainerEmail = "gnomino@hotmail.com"
lastupdated = "2006/Dec/31"
 footer = "Mutopia-2007/01/01-900"
 tagline = \markup { \override #'(box-padding . 1.0) \override #'(baseline-skip . 2.7) \box \center-column { \small \line { Sheet music from \with-url #"http://www.MutopiaProject.org" \line { \teeny www. \hspace #-1.0 MutopiaProject \hspace #-1.0 \teeny .org \hspace #0.5 } • \hspace #0.5 \italic Free to download, with the \italic freedom to distribute, modify and perform. } \line { \small \line { Typeset using \with-url #"http://www.LilyPond.org" \line { \teeny www. \hspace #-1.0 LilyPond \hspace #-1.0 \teeny .org } by \maintainer \hspace #-1.0 . \hspace #0.5 Reference: \footer } } \line { \teeny \line { This sheet music has been placed in the public domain by the typesetter, for details see: \hspace #-0.5 \with-url #"http://creativecommons.org/licenses/publicdomain" http://creativecommons.org/licenses/publicdomain } } } }

}


%% Tags the music expression with #'midi
ifmidi = #(define-music-function (parser location music) (ly:music?)
	#{ \tag #'midi $music #})


%% Tags music expression A with #'nmidi and the music expression B with #'midi
%% ("Ifelse midi")
%% Note: A & B cannot be switched, because lilypond (2.11.4) fails with a
%% programming error: minimise_least_squares ():  Nothing to minimise
%% and the music from point onwards is not laid out correctly.
%% (might have something to do with the extra open slur in the midi-only part)
ifemidi = #(define-music-function (parser location musicA musicB) (ly:music? ly:music?)
	#{ $musicA #})

violinOne = \new Voice {
	\set Staff.instrumentName = "violin-1"
	\set Staff.midiInstrument = "violin"
	\set Score.markFormatter = #format-mark-box-barnumbers
	\override MultiMeasureRest #'expand-limit = 1

	\clef treble
	\key g \major
	\time 4/4
	\tempo 4 = 144

	\relative g'' {

		%% primary theme

		g4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8\f r g4. b8( a) g-. %% "rocket theme"
		\appoggiatura {a16} g8( fis8) fis4. a8( c) fis,-.
		a( g) g4. b8( a) g-.
		\appoggiatura a16 g8( fis8) fis4. a8( c) fis,-.
		g-. g-. \appoggiatura g16 fis8( e16 fis) g8-. g-. \appoggiatura b16 a8( g16 a)
		b8-.\> b-. \appoggiatura d16 c8( b16 c) d4\p r

		d,2\p( e) %% piano
		\acciaccatura d8 c4 c \acciaccatura c8 b4 b
		\acciaccatura b8 a4 a g8( fis) e-. fis-.
		g8 r a r b r r4
		d2( e)
		d8( c) c-. c-. c( b) b-. b-.
		b( a) a-. a-. g( fis e fis)
		\grace g,16 g'2~\sf g8 g16\p\trill( fis32 g a8 fis) %% sforzando
|
		b2~\sf b8 b16\p\trill( a32 b c8 a)
		d16 d d d d d d d e\< e e e fis fis fis fis
		g16 g g g a a a a b b b b cis cis cis cis
		d4.\f a8 cis8.( a16) cis8.( a16) %% \forte
		d4.( a8) cis8.( a16) cis8.( a16)
		d8 d4 d d d8 ~ d d4 d d d8
		cis8 a d a cis a d a
		cis a, a a a4 r

		%% secondary theme
		
		 \mark \default
		a'4.\p( \times 2/3 { g16 fis e } d8) r b' r
		g r e r a r r4
		fis4.( \times 2/3 { e16 d cis } b8)  r g' r
		fis2( e4) r
		r8 a-. a-. a-. a-. a-. a-. a-.
		a-. a-. a-. a-. a-. a-. b-. cis-.
		cis( d) r b b( a) r cis,
		d4 r8 a'-.\mp d( cis b a)
		\pitchedTrill b\trill( cis a8) r a-. a-. a-. a-. a-.
		\pitchedTrill b\trill( cis a8) r a d( cis b a)
		\pitchedTrill b\trill( cis a8) r a-. a-. a-. a-. a-.
		\pitchedTrill b\trill( cis a8) r4 b4.\f \times 2/3 { a16( g fis }
		g4) r a4. \times 2/3 { g16( fis e }
		fis4) r b8( cis16 d cis8) b-.
		b( a) fis-. a-. a( g) fis-. e-.
		d4 r8 a'\p d( cis b a)
		\pitchedTrill b\trill( cis a8) r a-. a-. a-. a-. a-.
		\ifemidi { \pitchedTrill b\trill( cis } \times 2/3 { b16 cis b } a8) r a d( cis b a)
		\ifemidi { \pitchedTrill b\trill( cis } \times 2/3 { b16 cis b } a8) r a-. a-. a-. a-. a-.
		\ifemidi { \pitchedTrill b\trill( cis } \times 2/3 { b16 cis b } a8) r4 b4.\f \times 2/3 { a16( g fis }
		g4) r a4. \times 2/3 { g16( fis e }
		fis4) r b8( cis16 d cis8) b-.
		b( a) fis-. a-. a( g) fis-. e-.
		d a b cis d-. d-. \ifemidi { e\trill( } \times 2/3 { e16 fis e } d16 e %% tutti
		fis8) cis d e fis fis \ifemidi { g\trill( } \times 2/3 { g16 a g } fis16 g
		a8) a \ifemidi { ais\trill( } \times 2/3 { ais16 b ais } gis16 ais b4) r
		b,4.\p( e8) d( cis b a)
		d r fis r d r r4

		%% development

		
		 \mark \default
		d4\f r8 a d4 r8 a
		d a d fis a4 r
		a4 r8 fis a4 r8 fis
		a fis dis fis b,4 r
		
		r r8 g'8\mp c( b a g)
		\ifemidi { a\trill( } \times 2/3 { a16 b a } g8) r g-. g-. g-. g-. g-.
		\ifemidi { a\trill( } \times 2/3 { a16 b a } g8) r g c( b a g)
		\ifemidi { a\trill( } \times 2/3 { a16 b a } g8) r g g g g g
		\ifemidi { a\trill( } \times 2/3 { a16 b a } g8) r g c( b a g)
		\ifemidi { a\trill( } \times 2/3 { a16 b a } gis8) r gis gis gis gis gis
		\ifemidi { b\trill( } \times 2/3 { b16 c b } a8) r a c( bes a g)
		\ifemidi { g\trill( } \times 2/3 { g16 a g } fis8) r fis fis fis fis fis
		\ifemidi { a\trill( } \times 2/3 { a16 b a } g8) r es g( f es d)
		\ifemidi { d\trill( } \times 2/3 { d16 e d } cis8) r cis cis cis cis cis
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d,\f( e fis g a %% forte
		c bes) r fis( g a bes cis
		e d) r d\p( e fis g a
		bes4 b c cis)
		d1(
		d2) \ifemidi { fis,4.\trill( } \repeat unfold 6 { g32 fis } e16 fis)
		
		%% recapulation
		%% primary theme
		
		\mark \default %% no break (no rest)
		g4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8 r g4. b8( a) g-. %% "rocket theme"
		\ifemidi { g\trill( } { a32( g a g } fis8) fis4. a8( c) fis,-.
		a( g) g4. b8( a) g-.
		\ifemidi { g\trill( } { a32( g a g } fis8) fis4. a8( c) fis,-.
		g-. g-. \appoggiatura g16 fis8( e16 fis) g8-. g-. \appoggiatura b16 a8( g16 a)
		b8-. b-. \appoggiatura d16 c8( b16 c) d4 r
		d,2\p( e) %% piano
		\acciaccatura d8 c4 c \acciaccatura c8 b4 b
		\acciaccatura b8 a4 a g8( fis) e-. fis-.
		g8 r a r b r r4
		d2( e)
		d8( c) c-. c-. c( b) b-. b-.
		b( a) a-. a-. g( fis e fis)
		\grace g,16 g'2~\sf g8 \ifemidi { g16\p\trill( } { a32\p( g } fis32 g a8 fis) %% sforzando
		b2~\sf b8 \ifemidi { b16\p\trill( } { c32\p( b } a32 b c8 a)
		d16 d d d d d d d e\< e e e fis fis fis fis
		g g g g a a a a b b b b cis cis cis cis |
		d4.\f a8 cis8.( a16) cis8.( a16) %% \forte
		d4.( a8) cis8.( a16) cis8.( a16)
		d8-. a-. cis-. a-. d-. a-. cis-. a-.
		d d,, d d d4 r
		
		%% secondary theme
		
		 \mark \default
		d'4.\p( \times 2/3 { c16 b a } g8) r e' r
		c r a r d r r4
		b'4.( \times 2/3 { a16 g fis } e8)  r c' r
		b2( a4) r
		r8 d-. d-. d-. d-. d-. d-. d-.
		d-. d-. d-. d-. d( c a fis)
		fis( g) r e e( d) r fis,
		g4 r8 d'-. g( fis e d)
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d-. d-. d-. d-. d-.
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d g( fis e d)
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d-. d-. d-. d-. d-.
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r4 e4.\f \times 2/3 { d16( c b }
		c4) r d4. \times 2/3 { c16( b a }
		b4) r e8( fis16 g fis8) e-.
		e( d) b-. d-. d( c) b-. a-.
		g4 r8 d'-. g( fis e d)
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d-. d-. d-. d-. d-.
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d g( fis e d)
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r d-. d-. d-. d-. d-.
		\ifemidi { e\trill( } \times 2/3 { e16 fis e } d8) r4 e'4.\f \times 2/3 { d16( c b }
		c4) r d4. \times 2/3 { c16( b a }
		b4) r e,8( fis16 g fis8) e-.
		d-. g-. b-. d-. d( c) b-. a-.
		g d, e fis g g \ifemidi { a\trill( } \times 2/3 { a16 b a } g16 a %% tutti
		b8) fis g a b b \ifemidi { c\trill( } \times 2/3 { c16 d c } b16 c
		d8) d \ifemidi { dis\trill( } \times 2/3 { dis16 e dis } cis16 dis e4) r
		e,4.\p( a8) g( fis e d)
		d'( cis c b d cis c b)
		e,4.( a8) g( fis e d)
		d'( e fis g d e fis g)
		a4 r d\f r %% forte
		 \mark \default
		g, r8 d b g b d %% coda theme
		g d g b d4 fis,
		g r8 d b g b d
		g d g b d4 fis,
		g r g r
		g g,8. g16 g4 r


}}

violinTwo = \new Voice {
	\set Staff.instrumentName = "violin-2"
	\set Staff.midiInstrument = "violin"
	\set Score.markFormatter = #format-mark-box-barnumbers
	\override MultiMeasureRest #'expand-limit = 1

	\clef treble
	\key g \major
	\time 4/4
	\tempo 4 = 144

	\relative g'' {

		%% primary theme

		b,4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		b,16\p d b d b d b d 
		  b16 d b d b d b d 
		c16 d c d c d c d
		  c16 d c d c d c d
		b16 d b d b d b d 
		  b16 d b d b d b d 
		c16 d c d c d c d
		  c16 d c d c d c d
		b4-. c'8\< c d\mp d c( b16 a)
		g8\> g fis fis g4\p r

		b2\p( c) %% piano
		\acciaccatura b8 a4 a \acciaccatura a8 g4 g
		e4 e c a
		d8 r fis r g r r4
		b2( c)
		b8( a) a-. a-. a( g) g-. g-.
		e4 e8 e c4 c8 c
		b2~\sf b8 \ifemidi { b16\p\trill( } { c32\p b } a32 b c8 a) %% sforzando
		g'2~\sf g8 \ifemidi { g16\p\trill( } { a32\p g } fis32 g a8 fis)
		b16 b b b b b b b c\< c c c c c c c
		b16 b b b d d d d d d d d g g g g
		fis\mf fis fis fis fis fis fis fis g g g g g g g g |
		fis16 fis fis fis fis fis fis fis g g g g g g g g |
		fis8 fis4 fis fis fis8(
		e) e4 e e e8
		e16 e e e fis fis fis fis e e e e fis fis fis fis
		e8 a, a a a4 r

		%% secondary theme

		 \mark \default
		a4.\p( \times 2/3 { g16 fis e } d8) r b' r
		g r e r a r r4
		fis4.( \times 2/3 { e16 d cis } b8)  r g' r
		fis2( e4) r
		a4.( \times 2/3 { g16 fis e } d8) r b' r
		g r e r a r g r
		g( fis) r g' g( fis) r g,
		fis fis g g a a fis fis
		e e fis fis g g e e
		fis fis g g a a fis fis
		e e fis fis g g e e
		fis4 r fis'2\f(
		e4) r e2(
		d8) fis-. g-. a-. g( a16 b a8) g-.
		g( fis) d-. fis-. fis( e) d-. cis-.
		d fis,\p g g a a fis fis
		e e fis fis g g e e
		fis fis g g a a fis fis
		e e fis fis g g e e
		fis4 r fis'2\f(
		e4) r e2(
		d8) fis-. g-. a-. g( a16 b a8) g-.
		g( fis) d-. fis-. fis( e) d-. cis-.
		d a b cis d-. d-. \ifemidi { e\trill( } \times 2/3 { e16 fis e } d16 e %% tutti
		fis8) cis d e fis fis \ifemidi { g\trill( } \times 2/3 { g16 a g } fis16 g
		a8) a \ifemidi { ais\trill( } \times 2/3 { ais16 b ais } gis16 ais b4) r
		g,1\p(
		fis8) r a r fis r r4

		%% development

		 \mark \default
		d'4\f r8 a d4 r8 a
		d a d fis a4 r
		a4 r8 fis a4 r8 fis
		a fis dis fis b,4 r
		
		e,8\p e f f g g e e
		d d e e f f d d
		e e f f g g e e
		d d e e f f d d
		e e f f g g e e
		d d e e f f d d
		c c d d e e c c
		c c d d es es c c
		bes bes a a bes bes a' a
		bes bes a a bes bes a g
		fis4 r8 d\f( e fis g a %% forte
		c bes) r fis( g a bes cis
		e d) r d,\p( e fis g a
		bes4 b c cis)
		d8-. d-. d( e) c-. c-. c( d)
		b-. b-. b( d) d( c) b-. a-.
		
		%% recapulation
		%% primary theme
		
		\mark \default
		g4\f r8 d' g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		b16\p b b b b b b b b b b b b b b b
		c c c c c c c c c c c c c c c c |
		b16 b b b b b b b b b b b b b b b
		c c c c c c c c c c c c c c c c |		
		d4\mp c8 c d d c( b16 a)
		g8 g fis fis g4 r
		b2\p( c) %% piano
		\acciaccatura b8 a4 a \acciaccatura a8 g4 g
		e4 e c a
		d8 r fis r g r r4
		b2( c)
		b8( a) a-. a-. a( g) g-. g-.
		e4 e8 e c4 c8 c
		b2~\sf b8 \ifemidi { b16\p\trill( } { c32\p b } a32 b c8 a) %% sforzando
		g'2~\sf g8 \ifemidi { g16\p\trill( } { a32\p g } fis32 g a8 fis)
		b16 b b b b b b b c\< c c c c c c c |
		b b b b d d d d d d d d g g g g |
		fis\mf fis fis fis fis fis fis fis g g g g g g g g |
		fis fis fis fis fis fis fis fis g g g g g g g g |
		fis fis fis fis g g g g fis fis fis fis g g g g |
		fis8 d, d d d4 r
		
		%% secondary theme

		 \mark \default
		d4.\p( \times 2/3 { c16 b a } g8) r e' r
		c r a r d r r4
		b'4.( \times 2/3 { a16 g fis } e8)  r c' r
		b2( a4) r
		d4.( \times 2/3 { c16 b a } g8) r e' r
		c r a r d r c r
		c( b) r c c( b) r c,
		b b c c d d b b
		a a b b c c a a
		b b c c d d b b
		a a b b c c a a
		b4 r b'2\f(
		a4) r a2(
		g8) b-. c-. d-. c( d16 a d8) c-.
		c( b) g-. b-. b( a) g-. fis-.
		g b,\p c c d d b b
		a a b b c c a a
		b b' c c d d b b
		a a b b c c a a
		b4 r b'2\f(
		a4) r  a2(
		g8) b,-. c-. d-. c( d16 e d8) c-.
		b-. d-. g-. b-. b( a) g-. fis-.
		g d, e fis g g \ifemidi { a\trill( } \times 2/3 { a16 b a } g16 a %% tutti
		b8) fis g a b b \ifemidi { c\trill( } \times 2/3 { c16 d c } b16 c
		d8) d \ifemidi { dis\trill( } \times 2/3 { dis16 e dis } cis16 dis e4) r
		c,1\p(
		b4) r r2
		c1(
		b4) r b' r
		e r fis\f r %% forte
		 \mark \default
		b,16\mp b b b b b b b b b b b b b b b
		b b b b b b b b b b b b c c c c
		b16 b b b b b b b b b b b b b b b
		b b b b b b b b b b b b c c c c |
		d4 r b'\f r
		b g8. g16 g,4 r
		
		\bar "|."


}}


viola = \new Voice {
	\set Staff.instrumentName = "viola-1"
	\set Staff.midiInstrument = "viola"
	\set Score.markFormatter = #format-mark-box-barnumbers
	\override MultiMeasureRest #'expand-limit = 1

	\clef alto
	\key g \major
	\time 4/4
	\tempo 4=144

	\relative g' {

		%% primary theme

		g4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8\p g g g g g g g %% "rocket theme"
		a\< a a a a(\mp c) fis,(\> a)
		g\p g g g g g g g
		a\< a a a a(\mp c) fis,(\> a)
		d,16\p d d d d d d d
		  d16 d d d d d d d
		d16 d d d d d d d d4 r
		r1 %% piano
		fis,2\p( g)
		c4 c a d,
		d8 r d' r d r r4
		r1
		fis2( g)
		c,4 c8 c a4 a8 a
		g\sf g g g g\p g g g %% sforzando
		g\sf g g g g\p g g g
		g g' g g g\< g a a
		g g fis fis g g e e
		a16\mf a a a a a a a e e e e e e e e
		a a a a a a a a e e e e e e e e
|
		fis8 g a g fis g a fis
		b a g a b a gis b
		a a a a a a a a
		a a, a a a4 r

		%% secondary theme
		
		 \mark \default
		r2 r4 fis'8\p r
		b, r g' r e r cis r
		r4 e( d8)  r e r
		d2( cis4) r
		r cis( d8) r fis r
		b, r g r e r e' r
		e( d) r4 r2
		d8 d e e fis fis d d
		cis cis d d e e cis cis
		d d e e fis fis d d
		cis cis d d e e cis cis
		d d\f fis e dis b cis dis
		e g e d cis a b cis
		d d'\mf d d d d d d
		d( a) a-. a-. a a a g
		fis d\p e e fis fis d d
		cis cis d d e e cis cis
		d d e e fis fis d d
		cis cis d d e e cis cis
		d d\f fis e dis b cis dis
		e g e d cis a b cis
		d d'\mf d d d d d d
		d( a) a-. a-. a a a g
		fis a, b cis d d e e %% tutti
		fis cis d e fis fis g g
		a a ais ais b4 r
		e,2.\p( d8 cis)
		d r d r d r r4

		%% development

		
		 \mark \default
		d4\f r8 a d4 r8 a
		d a d fis a4 r
		a4 r8 fis a4 r8 fis
		a fis dis fis b,4 r
		
		c8\p c d d e e c c
		b b c c d d b b
		c c d d e e c c
		b b c c d d b b
		c c d d e e c c
		b b c c d d b b
		a a b b c c a a
		a a bes bes c c a a
		g g fis fis g g fis' fis
		g g fis fis g g, fis g
		a4 r8 d,\f( e fis g a %% forte
		c bes) r fis( g a bes cis
		e d) r4 r2
		r1
		b'8\p-. b-. b( c) a-. a-. a( b)
		g-. g-. g( b) b( a) g-. d-.
		
		%% recapulation
		%% primary theme
		
		\mark \default
		b4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8\mp g g g g g g g %% "rocket theme"
		a a a a a( c) fis,( a)
		g g g g g g g g
		a a a a a( c) fis,( a)
		d,16\p d d d d d d d d d d d d d d d |
		d8 d d d d4 r4
		r1 %% piano
		fis,2\p( g)
		c4 c a d,
		d8 r d' r d r r4
		r1
		fis2( g)
		c,4 c8 c a4 a8 a
		g\sf g g g g\p g g g %% sforzando
		g\sf g g g g\p g g g
		g g' g g g\< g a a
		g g fis fis g g e e
		a16\mf a a a a a a a e e e e e e e e
		a a a a a a a a e e e e e e e e
		a a a a e e e e a a a a e e e e |
		a8 d,, d d d4 r
		
		%% secondary theme
		
		 \mark \default
		r2 r4 b'8\p r
		e, r c' r a r fis r
		r4 a'( g8)  r a r
		g2( fis4) r
		r fis( g8) r b r
		e, r c r a r a' r
		a( g) r4 r2
		g,8 g a a b b g g
		fis fis g g a a fis fis
		g g a a b b g g
		fis fis g g a a fis fis
		g g'\f b a gis e fis gis
		a c a g fis d e fis
		g g\mf g g g g g g
		g( d) d-. d-. d d d c
		b g\p a a b b g g
		fis fis g g a a fis fis
		g g' a a b b g g
		fis fis g g a a fis fis
		g g\f b a gis e fis gis
		a c a g fis d e fis
		g g\mf g g g g g g
		g b d d d d d c
		b d, e fis g g a a %% tutti
		b fis, g a b b c c
		d d dis dis e4 r
		a,2.\p( g8 fis)
		g4 r r2
		a2.( g8 fis)
		g4 r g' r
		e r d\f r %% forte
		 \mark \default
		g,16\mp g g g g g g g g g g g g g g g 
		g g g g g g g g g g g g a a a a
		g g g g g g g g g g g g g g g g 
		g g g g g g g g g g g g a a a a |
		g8 b\f d g b g d' b
		g4 g,8. g16 g4 r
		
		\bar "|."

}}


cello = \new Voice {
	\set Staff.instrumentName = "cello-1"
	\set Staff.midiInstrument = "cello"
	\set Score.markFormatter = #format-mark-box-barnumbers
	\override MultiMeasureRest #'expand-limit = 1

	\clef bass
	\key g \major
	\time 4/4
	\tempo 4=144

	\relative g {

		%% primary theme

		g4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8\p g g g g g g g %% "rocket theme"
		g g g g g g g g
		g g g g g g g g
		g g g g g g g g
		g\< g a a b\mp b fis fis
		g\> g a a b4\p r
		r1 %% piano
		d,2\p( e)
		c4 c d d
		b8 r d r g r r4
		r1
		d2( e)
		c4 c d d
		g8\sf g g g g\p g g g %% sforzando
		g\sf g g g g\p g g g
		g g g g g\< g g g
		g g fis fis g g e e
		d1\mp
		d
		d8\mf e fis e d e fis d
		g a b a g a b gis
		a a a a a a a a
		a a, a a a4 r

		%% secondary theme
		
		 \mark \default
		r2 r4 dis8\p r
		e r d r cis r a r
		r4 ais( b8)  r g r
		a4 a'4.( gis8 g e) 
		d r e r fis r dis r
		e r d r cis r a r
		b r g' r a r a, r
		d4 r r2
		a4 r r2
		d4 r r2
		a4 r r2
		r8 d\f fis e dis b cis dis
		e g e d cis a b cis
		d d\mf e fis g g g g
		a a a a a, a a a
		d4 r r2
		a4\p r r2
		d4 r r2
		a4 r r2
		r8 d\f fis e dis b cis dis
		e g e d cis a b cis
		d d\mf e fis g g g g
		a a a a a, a a a
		d a b cis d d e e %% tutti
		fis8 cis d e fis fis g g
		a a ais ais b4 r
		g2\p( a)
		d,8 r d r d r r4

		%% development

		
		 \mark \default
		d4\f r8 a d4 r8 a
		d a d fis a4 r
		a4 r8 fis a4 r8 fis
		a fis dis fis b,4 r
		
		c4\p r r2
		g4 r r2
		c4 r r2
		g4 r r2
		c4 r r2
		e4 r r2
		a,4 r r2
		d4 r r2
		es1~
		es
		d4 r8 d\f( e fis g a %% forte
		c bes) r fis( g a bes cis
		e d) r4 r2
		r1*2
		d,1\p
		
		%% recapulation
		%% primary theme

		\mark \default
		g4\f r8 d g4 r8 d
		g d g b d4 r
		c4 r8 a c4 r8 a
		c a fis a d,4 r
		g8\mp g g g g g g g %% "rocket theme"
		g g g g g g g g
		g g g g g g g g
		g g g g g g g g
		g g a a b b fis fis
		g g a a b4 r
		r1 %% piano
		d,2\p( e)
		c4 c d d
		b8 r d r g r r4
		r1
		d2( e)
		c4 c d d
		g8\sf g g g g\p g g g %% sforzando
		g\sf g g g g\p g g g
		g g g g g\< g g g
		g g fis fis g g e e
		d1\mp
		d
		d8 d d d d d d d
		d d d d d4 r
		
		%% secondary theme
		
		 \mark \default
		r2 r4 gis8\p r
		a r g r fis r d r
		r4 dis( e8)  r c r
		d4 d'4.( cis8 c a) 
		g r a r b r gis r
		a r g r fis r d r
		e r c r d r d r
		g,4 r r2
		d'4 r r2
		g,4 r r2
		d'4 r r2
		r8 g\f b a gis e fis gis
		a c a g fis d e fis
		g-. g-.\mf a-. b-. c c c c
		d d d d d, d d d
		g4 r r2
		d4\p r r2
		g4 r r2
		d4 r r2
		r8 g\f b a gis e fis gis
		a c a g fis d e fis
		g-. g-.\mf a-. b-. c c c c
		d d d d d, d d d
		g d e fis g g a a %% tutti
		b fis g a b b c c
		d d dis dis e4 r
		c,2(\p d)
		g,4 r r2
		c( d)
		g,4 r r2
		c4 r d\f r %% forte
		 \mark \default
		g,8\mf g g g g g g g %% coda theme
		g g g g g g g g
		g g g g g g g g
		g g g g g g g g
		g b\f d g b g d' b
		g4 g,8. g16 g4 r
		
		\bar "|."


}}



mvtOne =
  %\articulate <<
  %<<
 \new StaffGroup <<
	\new GrandStaff <<
 		\violinOne
 		\violinTwo
	>>
	\viola
	\cello
>>

\book {
%	\header {
%		%\include "headers.ly"
%	}
	\score {
		\mvtOne
%		%\layout {}
   \layout{}
  \midi{}
	 }
%	\paper {
%		#(layout-set-absolute-staff-size (* 4.4 mm))
%		%%system-count = 20 %% can't do this for letter
%		ragged-bottom = ##f
%		ragged-last-bottom = ##f
%	}
}

%\book {
%	\score {
%		%\iftop \unfoldRepeats \withmidi \mvtOne
%		\midi {
%			\tempo 4 = 144
%		}
%	}
% }
