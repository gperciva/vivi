\version "2.14.0"

\include "vivi.ly"
\include "reduce-whitespace.ly"

violinone = \relative c' {
  \key d \major
  \tempo 4 = 96

  a4\f d fis8-. a-. r4
  d16(\downbow cis b a) g4 \breathe e8\p( g) fis4
%{
  e4\< g8 fis g4-_\mp\>
    \st "III"
    b8-_\startTextSpan a-_\stopTextSpan
    b4\p\<( d8 cis) d4(-. fis8-.^"II" e-.^"II")
  fis16(\mf\downbow g a b c\> b a g) fis(\upbow e d c) b(\downbow a g fis)
  e8-.\mp\upbow r e'-.\upbow^"tip" r e,4->^"mb" r4

  \key d \minor
  \time 3/4
  \tempo 4 = 120
  d4.\mf^"pizz." e8 f4
  f'4. e8 d4
  d,4.\mp c8 bes4
  \tempo 4 = 88
  a16\p e' a e' a,,32\f e' a e' r8 r4
  d4^"arco"^"lh"\> \acciaccatura { c8 } bes4 \acciaccatura { a8 } g4
  \st "III"
  fis16\p\startTextSpan a_"II" g a_"II" a a_"II" bes a_"II"
    c a_"II" bes a_"II"\stopTextSpan
  a4\breathe a,\breathe r4
%}
}

\score {
  <<
    \new Staff {
      \set Staff.instrumentName = "violin-1"
      \set Staff.midiInstrument = "violin"
      \violinone
    }
   >>
  \layout{}
  \midi{}
}

