\version "2.16.0"

\include "vivi.ly"
\include "reduce-whitespace.ly"

violinone = \relative c {
  \tempo 4 = 96
  \clef bass

  a8\ff d b d c d b d   % hill climbing

%  \st "III"
%  fis16\p\startTextSpan a_"II" g a_"II" a a_"II" bes a_"II"
%    c a_"II" bes a_"II"\stopTextSpan
%  a4\breathe a,\breathe r4

}

\score {
  <<
    \new Staff {
      %\set Staff.instrumentName = "violin-1"
      %\set Staff.midiInstrument = "violin"
      \set Staff.instrumentName = "cello-1"
      \set Staff.midiInstrument = "cello"
      \violinone
    }
   >>
  \layout{}
  \midi{}
}

