class SynapseLang < Formula
  include Language::Python::Virtualenv

  desc "Scientific programming language with quantum and uncertainty support"
  homepage "https://synapse-lang.org"
  url "https://files.pythonhosted.org/packages/source/s/synapse-lang/synapse-lang-2.2.0.tar.gz"
  sha256 "placeholder_will_be_updated_after_pypi_upload"
  license "MIT"
  head "https://github.com/synapse-lang/synapse-lang.git", branch: "main"

  depends_on "python@3.11"
  depends_on "numpy"
  depends_on "scipy"
  depends_on "openblas"

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/source/n/numpy/numpy-1.24.3.tar.gz"
    sha256 "ab344f1bf21f140adab8e47fdbc7c35a477dc01408791f8ba00d018dd0bc5155"
  end

  resource "scipy" do
    url "https://files.pythonhosted.org/packages/source/s/scipy/scipy-1.11.4.tar.gz"
    sha256 "90a2b78e7f5733b9de748f589f09225013685f9b218275257f8a8168c4e5ea5"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/python", "-c", "import synapse_lang; print(synapse_lang.__version__)"
    system "#{bin}/python", "-c", "from synapse_lang.backends import auto; print(auto())"

    # Test basic Synapse code execution
    (testpath/"test.syn").write <<~EOS
      let x = 10
      let y = 20
      let z = x + y
      print(z)
    EOS

    output = shell_output("#{bin}/synapse #{testpath}/test.syn 2>&1")
    assert_match "30", output
  end
end