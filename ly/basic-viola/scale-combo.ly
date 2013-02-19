\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "viola-1"
\relative c' {
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

g4\f a b c
g4\mf a b c
g4\mp a b c
g4\p a b c
\break

d\f e fis g
d\mf e fis g
d\mp e fis g
d\p e fis g
\break

a\f b c d
a\mf b c d
a\mp b c d
a\p b c d
\break

e\f fis g a
e\mf fis g a
e\mp fis g a
e\p fis g a

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

