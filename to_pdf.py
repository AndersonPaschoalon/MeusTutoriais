import glob
import os
import sys

import markdown
import pdfkit


def to_pdf(input_dir, output_file="documento_concatenado.pdf"):
    """
    Concatena arquivos Markdown de um diretório (em ordem alfabética)
    e gera um PDF, inserindo uma quebra de página após cada arquivo.

    Args:
        input_dir (str): Caminho para a pasta contendo os arquivos .md.
        output_file (str): Nome do arquivo PDF de saída.
    """

    # 1. Encontrar e ordenar os arquivos Markdown alfabeticamente
    # O uso de glob.glob garante que apenas arquivos .md sejam considerados.
    md_files = sorted(glob.glob(os.path.join(input_dir, "*.md")))

    if not md_files:
        return f"Erro: Nenhum arquivo .md encontrado na pasta '{input_dir}'. Verifique o caminho."

    full_markdown_content = ""

    # 2. Definir o CSS e o template HTML para garantir o "belo PDF" e a quebra de página
    # Usamos o CSS 'page-break-before: always' no elemento '.page-break' para forçar a quebra.
    html_template_start = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Documento Concatenado</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20mm; }
        h1, h2, h3, h4 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        pre, code { background-color: #f4f4f4; padding: 5px; border-radius: 3px; overflow-x: auto;}
        .page-break {
            /* Força a quebra de página em PDF */
            page-break-before: always;
            border-top: 2px dashed #ccc;
            margin-top: 50px;
            padding-top: 20px;
        }
    </style>
</head>
<body>
    """
    html_template_end = "</body></html>"

    # 3. Concatenar o conteúdo com o marcador de quebra de página
    for i, file_path in enumerate(md_files):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            filename = os.path.basename(file_path)

            # Adiciona o nome do arquivo como um título H1
            full_markdown_content += f"\n# {filename}\n\n"
            full_markdown_content += content

            # Adiciona a quebra de página (como um elemento HTML) após cada arquivo, exceto o último
            if i < len(md_files) - 1:
                full_markdown_content += '\n\n<div class="page-break"></div>\n\n'

        except Exception as e:
            print(
                f"Aviso: Não foi possível ler o arquivo {file_path}. Erro: {e}",
                file=sys.stderr,
            )

    # 4. Converter o Markdown concatenado para HTML
    html_content = markdown.markdown(full_markdown_content)
    final_html = html_template_start + html_content + html_template_end

    # 5. Converter o HTML final para PDF usando pdfkit
    try:
        pdfkit.from_string(final_html, output_file)
        return f"Sucesso: PDF '{output_file}' gerado com sucesso a partir de {len(md_files)} arquivos Markdown."
    except IOError:
        # Erro comum quando o wkhtmltopdf não está instalado ou no PATH
        return (
            f"Erro ao gerar o PDF. Verifique se as dependências estão instaladas. "
            f"O wkhtmltopdf (motor usado pelo pdfkit) DEVE estar instalado no seu sistema. "
            f"Tente instalá-lo e verifique se ele está no PATH."
        )
    except Exception as e:
        return f"Ocorreu um erro inesperado: {e}"

    # Importe a função que você acabou de definir


# from seu_modulo import to_pdf

caminho_da_pasta = "os/apostila-os"
nome_do_pdf = "Relatorio_Final.pdf"

# Crie a pasta e arquivos de exemplo para demonstração (se necessário)
# import os
# os.makedirs(caminho_da_pasta, exist_ok=True)
# with open(os.path.join(caminho_da_pasta, "02_detalhes.md"), "w") as f: f.write("# Detalhes\n\nConteúdo do arquivo 2.")
# with open(os.path.join(caminho_da_pasta, "01_introducao.md"), "w") as f: f.write("# Introdução\n\nInício da documentação.")

resultado = to_pdf(caminho_da_pasta, nome_do_pdf)
print(resultado)
