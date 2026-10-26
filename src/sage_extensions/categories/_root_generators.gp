(form, lengths) -> {
  my(n = matsize(form)[1], span = matrix(n, 0), kept = List());
  if (!n, return([]));
  forvec(v = vector(n),
    my(r = v~, square = v * form * r);
    if (square && content(r) == 1 && setsearch(lengths, abs(square)) && content(2 * form * r) % square == 0,
      my(coordinates = if (#span, matinverseimage(span, r), []~));
      if (!#coordinates || denominator(coordinates) != 1,
        listput(kept, r);
        span = mathnf(concat(span, r));
        if (span == matid(n), return(Vec(kept)))
      )
    )
  )
}
