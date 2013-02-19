\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "viola-1"
\relative c {
  \key g \major
  \clef alto
  %\tempo 4 = 108
  \tempo 4 = 72

c4\mp d e f
g4 a b c
d e f g
a b c d
c2 r2

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

