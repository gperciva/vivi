\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  %\tempo 4 = 108
  %\tempo 4 = 72
  \tempo 4 = 120

g4\f a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

