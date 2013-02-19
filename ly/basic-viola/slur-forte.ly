\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "viola-1"
\transpose g' c' \relative c' {
  \key g \major
  \tempo 4 = 120
  \clef alto

g4\f( a b c)
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

