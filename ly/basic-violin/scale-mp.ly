\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

g4\mp a b c
d e fis g
a b c d
e fis g a

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

