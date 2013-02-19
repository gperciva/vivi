\version "2.13.31"

vlnone = \new Staff {
\relative c' {
  \set Staff.instrumentName = "violin-1"
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

g4\mf a b c
d e fis g
a b c d
e fis g a
g2 r2

\bar "|."
}
}

vlntwo = \new Staff {
\relative c' {
  \set Staff.instrumentName = "violin-2"
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

r2 g4\mf a
b c d e
fis g a b
c d e fis
g2 r2

\bar "|."
}
}

\score {
  <<
     \vlnone
     \vlntwo
  >>
  \layout{}
  \midi{}
}

