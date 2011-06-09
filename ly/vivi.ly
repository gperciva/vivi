\version "2.13.57"

st =
#(define-music-function
  (parser location text)
  (string?)
#{
  \override TextSpanner #'style = #'line
  \override TextSpanner #'(bound-details right padding) = #-1
  \override TextSpanner #'(bound-details left stencil-align-dir-y)
=
    #CENTER
  \override TextSpanner #'(bound-details right text) =
    \markup { \draw-line #'(0 . -1) }
  \override TextSpanner #'(bound-details left text) = $text
#})


