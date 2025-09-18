class SynapseLang < Formula
  desc "Scientific programming language with quantum support"
  homepage "https://synapse-lang.org"
  url "https://github.com/synapse-lang/synapse-lang/archive/v2.2.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.10"
  depends_on "numpy"
  depends_on "scipy"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#<built-in function bin>/synapse", "--version"
  end
end
