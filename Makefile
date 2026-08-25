PYTHON ?= python3
CXX ?= c++

.PHONY: test-fast test-full verify-cubic paper clean

test-fast:
	$(PYTHON) -m unittest tests.test_certificates tests.test_matrix_structural -v

test-full:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

verify-cubic:
	$(CXX) -O3 -std=c++17 tools/verify_relative_cubic.cpp -o /tmp/verify-relative-cubic
	/tmp/verify-relative-cubic

paper:
	cd submission && tectonic --keep-logs main.tex

clean:
	$(RM) submission/main.aux submission/main.log submission/main.out submission/main.pdf
