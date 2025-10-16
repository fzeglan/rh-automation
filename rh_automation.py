import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

class AutomacaoRH:
    def __init__(self, config_file='config_rh.json'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def triagem_candidatos(self, arquivo_cvs):
        df = pd.read_csv(arquivo_cvs)
        
        criterios = self.config['criterios']
        candidatos_aprovados = []
        candidatos_reprovados = []
        
        print("🔍 Iniciando triagem de candidatos...")
        print(f"📊 Total de candidatos: {len(df)}")
        print(f"🎯 Critérios: {criterios}\n")
        
        for _, candidato in df.iterrows():
            score = 0
            
            if candidato['experiencia_anos'] >= criterios['experiencia_minima']:
                score += 30
                print(f"✅ {candidato['nome']}: +30 pontos (experiência)")
            else:
                print(f"❌ {candidato['nome']}: 0 pontos (experiência insuficiente)")
            
            if criterios['educacao_minima'] in candidato['formacao']:
                score += 20
                print(f"✅ {candidato['nome']}: +20 pontos (formação)")
            else:
                print(f"❌ {candidato['nome']}: 0 pontos (formação abaixo do requerido)")
            
            habilidades_candidato = [h.strip() for h in candidato['habilidades'].split(',')]
            habilidades_match = set(habilidades_candidato) & set(criterios['habilidades_requeridas'])
            pontos_habilidades = len(habilidades_match) * 10
            score += pontos_habilidades
            
            print(f"🛠️  {candidato['nome']}: +{pontos_habilidades} pontos ({len(habilidades_match)} habilidades compatíveis)")
            print(f"📈 Score final: {score} pontos\n")
            
            if score >= criterios['score_minimo']:
                candidatos_aprovados.append({
                    'nome': candidato['nome'],
                    'email': candidato['email'],
                    'score': score,
                    'experiencia': candidato['experiencia_anos'],
                    'habilidades_match': list(habilidades_match)
                })
            else:
                candidatos_reprovados.append({
                    'nome': candidato['nome'],
                    'email': candidato['email'],
                    'score': score
                })
        
        return candidatos_aprovados, candidatos_reprovados
    
    def enviar_email_contato(self, candidato, aprovado=True):
        if aprovado:
            assunto = self.config['email_template']['assunto_aprovado']
            corpo = f"""
            Prezado(a) {candidato['nome']},
            
            Parabéns! Seu perfil foi selecionado para a próxima fase do processo seletivo.
            
            **Seu score:** {candidato['score']}/100
            **Experiência:** {candidato['experiencia']} anos
            **Habilidades compatíveis:** {', '.join(candidato['habilidades_match'])}
            
            Em breve nossa equipe entrará em contato para agendar a próxima etapa.
            
            Atenciosamente,
            Departamento de RH - {self.config['empresa']}
            """
        else:
            assunto = self.config['email_template']['assunto_reprovado']
            corpo = f"""
            Prezado(a) {candidato['nome']},
            
            Agradecemos seu interesse em fazer parte da {self.config['empresa']}.
            
            Após análise cuidadosa do seu perfil, infelizmente não poderemos 
            dar continuidade ao seu processo seletivo neste momento.
            
            Seu currículo ficará armazenado em nosso banco de dados e 
            entraremos em contato caso surjam oportunidades compatíveis.
            
            Desejamos sucesso em sua busca!
            
            Atenciosamente,
            Departamento de RH - {self.config['empresa']}
            """
        
        print(f"📧 Simulando envio de email para: {candidato['email']}")
        print(f"📨 Assunto: {assunto}")
        print(f"👤 Candidato: {candidato['nome']}")
        print(f"🎯 Status: {'Aprovado' if aprovado else 'Reprovado'}")
        print("---")
    
    def gerar_relatorio_txt(self, aprovados, reprovados):
        """Gera relatório em arquivo de texto"""
        os.makedirs('relatorios', exist_ok=True)
        
        arquivo_saida = 'relatorios/relatorio_triagem.txt'
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("RELATÓRIO DE TRIAGEM - RECRUTAMENTO\n")
            f.write("="*50 + "\n\n")
            
            f.write(f"Candidatos aprovados: {len(aprovados)}\n")
            f.write(f"Candidatos reprovados: {len(reprovados)}\n")
            
            total_candidatos = len(aprovados) + len(reprovados)
            if total_candidatos > 0:
                taxa_aprovacao = (len(aprovados) / total_candidatos) * 100
                f.write(f"Taxa de aprovação: {taxa_aprovacao:.1f}%\n\n")
            
            f.write("TOP CANDIDATOS APROVADOS:\n")
            for i, cand in enumerate(sorted(aprovados, key=lambda x: x['score'], reverse=True)[:5], 1):
                f.write(f"{i}º - {cand['nome']} (Score: {cand['score']})\n")
                f.write(f"   Email: {cand['email']}\n")
                f.write(f"   Experiência: {cand['experiencia']} anos\n")
                f.write(f"   Habilidades compatíveis: {', '.join(cand['habilidades_match'])}\n\n")
        
        print(f"📄 Relatório salvo em: {arquivo_saida}")
    
    def gerar_relatorio_terminal(self, aprovados, reprovados):
        """Relatório no terminal (mantido do original)"""
        print("\n" + "="*50)
        print("📊 RELATÓRIO FINAL DA TRIAGEM")
        print("="*50)
        print(f"✅ Candidatos aprovados: {len(aprovados)}")
        print(f"❌ Candidatos reprovados: {len(reprovados)}")
        
        total_candidatos = len(aprovados) + len(reprovados)
        if total_candidatos > 0:
            taxa_aprovacao = (len(aprovados) / total_candidatos) * 100
            print(f"📈 Taxa de aprovação: {taxa_aprovacao:.1f}%")
        
        if aprovados:
            print("\n🏆 TOP CANDIDATOS APROVADOS:")
            for i, cand in enumerate(sorted(aprovados, key=lambda x: x['score'], reverse=True)[:3], 1):
                print(f"{i}º - {cand['nome']} (Score: {cand['score']})")

if __name__ == "__main__":
    rh = AutomacaoRH('config_rh.json')
    
    aprovados, reprovados = rh.triagem_candidatos('candidatos.csv')
    
    rh.gerar_relatorio_terminal(aprovados, reprovados)
    rh.gerar_relatorio_txt(aprovados, reprovados)
    
    print("\n🚀 ENVIANDO EMAILS PARA APROVADOS:")
    for candidato in aprovados:
        rh.enviar_email_contato(candidato, aprovado=True)
    
    print("\n📝 ENVIANDO EMAILS PARA REPROVADOS:")
    for candidato in reprovados:
        rh.enviar_email_contato(candidato, aprovado=False)