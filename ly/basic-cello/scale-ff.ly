\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "cello-1"
\relative c, {
  \key c \major
  \clef bass
  %\tempo 4 = 108
  \tempo 4 = 60

c4\ff d e f
g4 a b c
d e f g
a b c d
e d c2

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

