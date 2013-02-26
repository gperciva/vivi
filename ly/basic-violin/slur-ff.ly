\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\ff( a b c)
d4( e fis g)
a4( b c d)
e4( fis g a
b a g2)

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

