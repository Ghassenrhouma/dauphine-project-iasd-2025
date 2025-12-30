"""Script d'exploration des données TelecomPlus"""
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))


class DataExplorer:
    """Classe pour explorer les données du projet"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.xlsx_dir = self.data_dir / "xlsx"
        self.pdf_dir = self.data_dir / "pdfs"
        self.excel_files = {
            "clients": "clients.xlsx",
            "forfaits": "forfaits.xlsx",
            "abonnements": "abonnements.xlsx",
            "consommation": "consommation.xlsx",
            "factures": "factures.xlsx",
            "tickets": "tickets_support.xlsx",
        }
        self.eval_file = self.data_dir / "evaluation_questions.xlsx"
        self.data = {}
    
    def print_separator(self, char="-", length=80):
        """Affiche un séparateur"""
        print(char * length)
    
    def load_all_data(self):
        """Charge tous les fichiers Excel"""
        print("\n" + "=" * 80)
        print("CHARGEMENT DES DONNÉES")
        print("=" * 80 + "\n")
        
        loaded = 0
        
        # Charger les fichiers du dossier xlsx
        for name, filename in self.excel_files.items():
            filepath = self.xlsx_dir / filename
            
            if filepath.exists():
                try:
                    df = pd.read_excel(filepath)
                    self.data[name] = df
                    print(f"[OK] xlsx/{filename:<30} {len(df):>5} lignes")
                    loaded += 1
                except Exception as e:
                    print(f"[ERREUR] xlsx/{filename:<30} {str(e)}")
                    self.data[name] = None
            else:
                print(f"[NON TROUVÉ] xlsx/{filename}")
                self.data[name] = None
        
        # Charger le fichier d'évaluation
        if self.eval_file.exists():
            try:
                df = pd.read_excel(self.eval_file)
                self.data["evaluation"] = df
                print(f"[OK] {self.eval_file.name:<35} {len(df):>5} lignes")
                loaded += 1
            except Exception as e:
                print(f"[ERREUR] {self.eval_file.name:<35} {str(e)}")
                self.data["evaluation"] = None
        
        total_files = len(self.excel_files) + 1
        print(f"\nRésultat: {loaded}/{total_files} fichiers chargés avec succès")
    
    def analyze_table(self, table_name, display_name):
        """Analyse générique d'une table"""
        if table_name not in self.data or self.data[table_name] is None:
            return
        
        df = self.data[table_name]
        
        print("\n" + "=" * 80)
        print(f"ANALYSE: {display_name}")
        print("=" * 80)
        
        print(f"\nNombre d'enregistrements: {len(df)}")
        print(f"Nombre de colonnes: {len(df.columns)}")
        print(f"Colonnes: {list(df.columns)}")
        
        print("\nTypes de données:")
        print(df.dtypes)
        
        print("\nValeurs manquantes:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(missing[missing > 0])
        else:
            print("Aucune valeur manquante")
        
        print("\nAperçu des données (5 premières lignes):")
        print(df.head())
        
        print("\nStatistiques descriptives:")
        print(df.describe(include='all'))
    
    def analyze_clients(self):
        """Analyse de la table clients"""
        self.analyze_table("clients", "TABLE CLIENTS")
        
        if "clients" in self.data and self.data["clients"] is not None:
            df = self.data["clients"]
            
            if 'ville' in df.columns:
                print("\nRépartition par ville (top 10):")
                print(df['ville'].value_counts().head(10))
            
            if 'email' in df.columns and df['email'].notna().any():
                print("\nDomaines email (top 5):")
                domains = df['email'].str.split('@').str[1].value_counts().head(5)
                print(domains)
    
    def analyze_forfaits(self):
        """Analyse de la table forfaits"""
        self.analyze_table("forfaits", "TABLE FORFAITS")
        
        if "forfaits" in self.data and self.data["forfaits"] is not None:
            df = self.data["forfaits"]
            
            if 'prix_mensuel' in df.columns:
                print("\nAnalyse des prix:")
                print(f"Prix minimum: {df['prix_mensuel'].min():.2f} EUR")
                print(f"Prix maximum: {df['prix_mensuel'].max():.2f} EUR")
                print(f"Prix moyen: {df['prix_mensuel'].mean():.2f} EUR")
                print(f"Prix médian: {df['prix_mensuel'].median():.2f} EUR")
            
            if 'data_mensuelle_go' in df.columns:
                print("\nAnalyse de la data:")
                print(f"Data minimum: {df['data_mensuelle_go'].min()} Go")
                print(f"Data maximum: {df['data_mensuelle_go'].max()} Go")
                print(f"Data moyenne: {df['data_mensuelle_go'].mean():.2f} Go")
    
    def analyze_abonnements(self):
        """Analyse de la table abonnements"""
        self.analyze_table("abonnements", "TABLE ABONNEMENTS")
        
        if "abonnements" in self.data and self.data["abonnements"] is not None:
            df = self.data["abonnements"]
            
            if 'statut' in df.columns:
                print("\nRépartition par statut:")
                print(df['statut'].value_counts())
                print("\nPourcentages:")
                print(df['statut'].value_counts(normalize=True) * 100)
            
            if 'forfait_id' in df.columns:
                print("\nForfaits les plus souscrits:")
                print(df['forfait_id'].value_counts().head(10))
    
    def analyze_consommation(self):
        """Analyse de la table consommation"""
        self.analyze_table("consommation", "TABLE CONSOMMATION")
        
        if "consommation" in self.data and self.data["consommation"] is not None:
            df = self.data["consommation"]
            
            if 'data_utilisee_go' in df.columns:
                print("\nStatistiques de consommation data:")
                print(f"Minimum: {df['data_utilisee_go'].min():.2f} Go")
                print(f"Maximum: {df['data_utilisee_go'].max():.2f} Go")
                print(f"Moyenne: {df['data_utilisee_go'].mean():.2f} Go")
                print(f"Total: {df['data_utilisee_go'].sum():.2f} Go")
            
            if 'minutes_utilisees' in df.columns:
                print("\nStatistiques des minutes:")
                print(f"Minimum: {df['minutes_utilisees'].min()} min")
                print(f"Maximum: {df['minutes_utilisees'].max()} min")
                print(f"Moyenne: {df['minutes_utilisees'].mean():.2f} min")
                print(f"Total: {df['minutes_utilisees'].sum()} min")
            
            if 'sms_utilises' in df.columns:
                print("\nStatistiques des SMS:")
                print(f"Minimum: {df['sms_utilises'].min()}")
                print(f"Maximum: {df['sms_utilises'].max()}")
                print(f"Moyenne: {df['sms_utilises'].mean():.2f}")
                print(f"Total: {df['sms_utilises'].sum()}")
    
    def analyze_factures(self):
        """Analyse de la table factures"""
        self.analyze_table("factures", "TABLE FACTURES")
        
        if "factures" in self.data and self.data["factures"] is not None:
            df = self.data["factures"]
            
            if 'montant_total' in df.columns:
                print("\nAnalyse des montants:")
                print(f"Minimum: {df['montant_total'].min():.2f} EUR")
                print(f"Maximum: {df['montant_total'].max():.2f} EUR")
                print(f"Moyenne: {df['montant_total'].mean():.2f} EUR")
                print(f"Médiane: {df['montant_total'].median():.2f} EUR")
                print(f"Total: {df['montant_total'].sum():.2f} EUR")
            
            if 'statut_paiement' in df.columns:
                print("\nRépartition par statut de paiement:")
                print(df['statut_paiement'].value_counts())
                
                if 'montant_total' in df.columns:
                    print("\nMontants par statut:")
                    print(df.groupby('statut_paiement')['montant_total'].agg(['sum', 'mean', 'count']))
    
    def analyze_tickets(self):
        """Analyse de la table tickets"""
        self.analyze_table("tickets", "TABLE TICKETS SUPPORT")
        
        if "tickets" in self.data and self.data["tickets"] is not None:
            df = self.data["tickets"]
            
            if 'categorie' in df.columns:
                print("\nRépartition par catégorie:")
                print(df['categorie'].value_counts())
            
            if 'statut' in df.columns:
                print("\nRépartition par statut:")
                print(df['statut'].value_counts())
            
            if 'priorite' in df.columns:
                print("\nRépartition par priorité:")
                print(df['priorite'].value_counts())
            
            if 'categorie' in df.columns and 'statut' in df.columns:
                print("\nTableau croisé catégorie x statut:")
                print(pd.crosstab(df['categorie'], df['statut'], margins=True))
    
    def analyze_evaluation_questions(self):
        """Analyse des questions d'évaluation"""
        self.analyze_table("evaluation", "QUESTIONS D'ÉVALUATION")
        
        if "evaluation" in self.data and self.data["evaluation"] is not None:
            df = self.data["evaluation"]
            
            print("\nExemples de questions:")
            for i in range(min(5, len(df))):
                print(f"\nQuestion {i+1}:")
                print(f"  Q: {df.iloc[i].get('question', 'N/A')}")
                if 'expected_answer' in df.columns:
                    answer = str(df.iloc[i].get('expected_answer', 'N/A'))
                    print(f"  R: {answer[:200]}...")
    
    def analyze_pdfs(self):
        """Analyse des fichiers PDF"""
        print("\n" + "=" * 80)
        print("ANALYSE DES FICHIERS PDF")
        print("=" * 80)
        
        if not self.pdf_dir.exists():
            print(f"\nDossier '{self.pdf_dir}' non trouvé")
            return
        
        pdfs = sorted(list(self.pdf_dir.glob("*.pdf")))
        
        print(f"\nNombre total de PDFs: {len(pdfs)}\n")
        
        for i, pdf in enumerate(pdfs, 1):
            size_kb = pdf.stat().st_size / 1024
            print(f"{i:2d}. {pdf.name:<50} ({size_kb:>8.2f} KB)")
    
    def generate_summary(self):
        """Génère un résumé des données"""
        print("\n" + "=" * 80)
        print("RÉSUMÉ DES DONNÉES")
        print("=" * 80)
        
        summary_data = []
        
        tables = ["clients", "forfaits", "abonnements", "consommation", "factures", "tickets", "evaluation"]
        
        for table in tables:
            if table in self.data and self.data[table] is not None:
                df = self.data[table]
                summary_data.append({
                    'Table': table,
                    'Lignes': len(df),
                    'Colonnes': len(df.columns)
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            print("\n" + summary_df.to_string(index=False))
        
        if self.pdf_dir.exists():
            n_pdfs = len(list(self.pdf_dir.glob("*.pdf")))
            print(f"\nNombre de fichiers PDF: {n_pdfs}")
        
        print("\n" + "=" * 80)
    
    def run_full_exploration(self):
        """Lance l'exploration complète"""
        print("\n" + "=" * 80)
        print("EXPLORATION DES DONNÉES - PROJET TELECOMPLUS")
        print("=" * 80)
        
        self.load_all_data()
        self.analyze_clients()
        self.analyze_forfaits()
        self.analyze_abonnements()
        self.analyze_consommation()
        self.analyze_factures()
        self.analyze_tickets()
        self.analyze_evaluation_questions()
        self.analyze_pdfs()
        self.generate_summary()
        
        print("\nEXPLORATION TERMINÉE")
        print("=" * 80 + "\n")


def main():
    """Point d'entrée principal"""
    explorer = DataExplorer()
    explorer.run_full_exploration()


if __name__ == "__main__":
    main()