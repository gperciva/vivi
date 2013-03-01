\version "2.16.0"

#(set-global-staff-size 16)

%\include "../reduce-whitespace.ly"
%\include "articulate.ly"

\header {
}


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

		g1\ff
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
		b,1\mf
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
		d1\p

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
		g,1\f
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
