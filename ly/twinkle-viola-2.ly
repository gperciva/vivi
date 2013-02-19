\version "2.16.0"

\include "event-listener.ly"
\include "reduce-whitespace.ly"

\header {
  title = "Twinkle, Twinkle, Little Star"
  composer = "arr. Shinichi Suzuki"
}

vlnone = \new Staff {
  \transpose c' c'' {
  \set Staff.instrumentName = "viola-2"
  \tempo 4=88
  \key d \major
  \clef alto

  d4\f\downbow d\upbow a a
  b4 b a2
  g4 g fis fis
  e4 e d2

  a4 a g g
  fis fis e2
  a4 a g g
  fis fis e2
  
  d4\f d a a
  b4 b a2
  g4 g fis fis
  e4 e d2

  \bar "|."
} }

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

