#!/usr/bin/env python3
"""
Migrate missing high-priority content from legacy website to Jekyll archive.
Excludes champions_v1.html and Officers.htm as requested.
"""

import os
import shutil
from pathlib import Path

def migrate_files():
    """Migrate missing files from legacy to Jekyll archive."""
    
    legacy_path = "/mnt/c/Documents and Settings/samco/OneDrive/Organizations/Penguin Class/2024-08 penguinclass.com cleanup/httpdocs/"
    jekyll_archive_path = "archive/legacy-website/"
    
    # Files to exclude
    exclude_files = {
        'champions_v1.html',
        'Officers.htm'
    }
    
    # High priority files to migrate (from comparison results)
    high_priority_files = [
        # Regatta Results
        '2012_intls_results.htm',
        '2018_tcpfr_results_web.htm',
        
        # NOR (Notice of Race) files
        '2010 INTL Penguin NOTICE OF RACE_r2.htm',
        '2010TAYC_spring_NOR.htm',
        '2010_ICPFR NOR.htm',
        '2011 INTL Penguin NOTICE OF RACE.htm',
        '2011 Island Creek Penguin Frostbite Regatta_csk.htm',
        '2011 Spring SLPF.htm',
        '2012_GIYS_nor.htm',
        '2012_ICPFR NOR.htm',
        '2012_SLPF_spring.htm',
        '2013_ICPFR NOR.htm',
        '2013_Penguin Natls NOR  2.htm',
        '2014 PRSA pres_cup info.htm',
        '2014_GIYS_nor.htm',
        '2014_IPCDA Annual Meeting.htm',
        '2014_RunyonColie.htm',
        '2014_TCPFR Trippes Creek Penguin Frostbite Regatta.htm',
        '2014_trippeckpfr.htm',
        '2015 INTL Penguin NOTICE OF RACEv1.htm',
        '2015_GIYS_nor.htm',
        '2015_TCPFR Trippes Creek Penguin Frostbite Regatta.htm',
        '2016_GIYS_nor.htm',
        '2016_TCPFR Trippes Creek Penguin Frostbite Regatta.htm',
        '2017 INTL Penguin NOTICE OF RACE.htm',
        '2017_GIYS_nor.htm',
        '2017_TCPFR Trippes Creek Penguin Frostbite Regatta - NOR.htm',
        '2018 INTL Penguin NOTICE OF RACE.htm',
        '2018_Gibson Island Penguin Frostbite NOR.htm',
        '2018_TCPFR Trippes Creek Penguin Frostbite Regatta - NOR.htm',
        '2019 Corsica Annual Regatta.htm',
        '2019_TAYC Atlantic Coast.htm',
        '2021_CRYC_Turkey Trot_NOR.htm',
        '2021_Comet and Penguin Invitational.htm',
        '2021_GIYS_nor.htm',
        '2022 Comet and Penguin Invitational (1).htm',
        '2022_TAYC Frostbite.htm',
        '2023 Turkey Trotl NOR.htm',
        '2023_CRYC Annual Regatta NOR.htm',
        '2023_TAYC_Annual.htm',
        '2023_TAYC_Annual_1.htm',
        '2025_Corsica Annual NOR.htm',
        '2025_Intls_NOR.pdf.htm',
        
        # Other important regatta files
        '2006_ISLAND_CREEK_PENGUIN_FROSTBITE_REGATTA__.html',
        '2007_international_champions.htm',
        '2007_intls_entry_form.htm',
        '2007_intls_nor.htm',
        '2008_cbyra_highpoint.htm',
        '2008_frostbite_highpoint.htm',
        '2008_intls_notice_of_race.htm',
        '2008_maple_hall.htm',
        '2008_tayc_classic.htm',
        '2009_corsica.htm',
        '2009_minutes.htm',
        '2009_slpf_schedule.htm',
        '2010_AnnualMtg_Minutes.htm',
        '2010_InternationalsPhotos_link.htm',
        '2010_Penguin Frostbite.htm',
        '2010_Presidents Cup.htm',
        '2010_SLPF Fall Series.htm',
        '2010_SLPF_10_3.htm',
        '2010_TAYC Annual.htm',
        '2010_TAYC_Penguin Frostbite.htm',
        '2010_TAYC_spring.htm',
        '2010_prsa_memorial_day.htm',
        '2010_tayc_summer_invitational.htm',
        '2011_MRYC.htm',
        '2011_Miles River Annual Regatta.htm',
        '2011_PenguinRumBucket Results.html',
        '2011_President.htm',
        '2011_TAYC Frostbite.htm',
        '2011_TAYC_Annual.htm',
        '2011_TAYC_Penguin Invitational.htm',
        '2011_TAYC_summer.htm',
        '2011_dues.doc',
        '2011_slpf_fall.htm',
        '2012_Corsica.htm',
        '2012_Heritage Regatta.htm',
        '2012_NSHOF.htm',
        '2012_PotomacPenguin.htm',
        '2012_TAYC_Spring Invitational.htm',
        '2012_TAYCannualPenguin.htm',
        '2012_dues.htm',
        '2012_rum bucket results.htm',
        '2012_tayc_summer.htm',
        '2013 International Penguin Championship.htm',
        '2013_Bartlett breaks through.htm',
        '2013_Corsica River Yacht Club.htm',
        '2013_Gibson Island Yacht Squadron.htm',
        '2013_Heritage Regatta.htm',
        '2013_MRYC_Annual_summary.htm',
        '2013_Oxford Summer Regatta.htm',
        '2013_Potomac River Sailing Association.htm',
        '2013_TAYC_Annual_Penguin.htm',
        '2013_TAYC_Spring Invitational.htm',
        '2013_TAYC_frostbite.htm',
        '2014-TAYC AnnualPenguin.htm',
        '2014Gibson Island Yacht Squadron.htm',
        '2014Potomac Penguin Fleet Frostbite.htm',
        '2014_CRYC Penguin Internationals.pdf',
        '2014_Corsica Annual.htm',
        '2014_Internationals_Capital_Annapolis.htm',
        '2014_PotomacPresCup.htm',
        '2014_TAYC Summer.htm',
        '2015_Corsica River Yacht Club.htm',
        '2015_Gibson Island Yacht Squadron Penguin Frostbite.htm',
        '2015_PRSA_spring.htm',
        '2015_PresidentCup.htm',
        '2015_TAYC_Annual Penguin.htm',
        '2015_TAYC_Penguin Frostbite.htm',
        '2015_TAYC_Spring Invitational.htm',
        '2015_Trippe Creek Frostbite.htm',
        '2015_intls_results.htm',
        '2016 GIYS Lawson Rum Bucket.htm',
        '2016_Corsica River Yacht Club.htm',
        '2016_Internationals_results.htm',
        '2016_NSHOF.htm',
        '2016_PRSA_MemDay.htm',
        '2016_PRSA_prescup.htm',
        '2016_TAYC Annual Regatta.htm',
        '2016_TAYC Spring Invitational.htm',
        '2016_TAYC_Penguin Frostbite.htm',
        '2016_Trippe Creek Regatta_summary_w pictures.htm',
        '2017 Internationals results.htm',
        '2017 Potomac Frostbite.htm',
        '2017_Corsica River Yacht Club results.htm',
        '2017_GIYS.htm',
        '2017_TAYC Heritage.htm',
        '2017_TAYC Penguin Frostbite.htm',
        '2017_TAYC_Annual_results.htm',
        '2017_TAYC_Spring Invitational.htm',
        '2017_TCPRF_results.htm',
        '2018 Gibson Island Penguin Frostbite_Summary.htm',
        '2018 Penguin Internationals_Summary.htm',
        '2018_Heritage_summary.htm',
        '2018_Intls_results.htm',
        '2018_PRSA_presidents_cup.htm',
        '2018_TAYC Annual Penguin.htm',
        '2018_TAYC_Spring Invitational.htm',
        '2018_TCPFR_summary.htm',
        '2019_Internationals.htm',
        '2019_MRYC.htm',
        '2019_Pres Cup_Greetings PRSA sailors.htm',
        '2019_TAYC Annual.htm',
        '2019_TAYCPenguin and Comet Frostbite.htm',
        '2019_TAYC_Spring Invitational.htm',
        '2020_Oxford Annual Regatta.htm',
        '2020_TAYC frostbite.htm',
        '2021 Admiral Byrd Regatta.htm',
        '2021 Corsica River Yacht Club Turkey Trot Regatta.htm',
        '2021 Internationals.htm',
        '2021 Lawson Rum Bucket_Summary.htm',
        '2021_Bay Ridge Penguin Regatta.htm',
        '2021_Corsica River_Annual.htm',
        '2021_Heritage.htm',
        '2021_MRYC.htm',
        '2021_TAYC_Penguin and Comet Frostbite.htm',
        '2021_TAYC_annualPenguin.htm',
        '2021schedule.html',
        '2022 Penguin Internationals.htm',
        '2022 TAYC Heritage.htm',
        '2022_Corsica River Annual.htm',
        '2022_TAYC Annual Regatta (1).htm',
        '2022schedule.html',
        '2023 GIYS Comet and Penguin Invitational.pdf',
        '2023 Penguin Internationals _summary.htm',
        '2023 Penguin Internationals.htm',
        '2023 TAYC Frostbite and Region III Championship.htm',
        '2023_Beachwood.htm',
        '2023_CorsicaAnnualResults.htm',
        '2023_TAYC_Annual.htm',
        '2023_TAYC_Annual_photo.htm',
        '2024 Penguin Internationals.htm',
        '2024 TAYC Annual.htm',
        '2024 TAYC Heritage.htm',
        '2025_Beachwood Revival;.htm',
        '2025_Cambridge.htm',
        'Beachwood Penguin Revival.htm',
        
        # Important documents
        'NOR 2014 Internationals.htm',
        'NOR 2021 Internationals rev (1).htm',
        'NOR 2021 Internationals.htm',
        'NOR_intls2007.htm',
        'MRYC_2008_NOR,_Annual_One_Design_(2).htm',
        'PENGUIN FROSTBITE HIGH POINTS SCORING 2005.htm',
        'Penguin Internationals 2015.htm',
        'Sail_Specification.html',
        'JuniorWaiver_2014.htm',
        'JuniorWaiver_2017.htm',
        'JuniorWaiver_2018.htm',
        'Penguin flyer_David Green.htm',
        'WRSC_2005.htm',
        'bristol.htm',
        'cbyra05.htm',
        'cbyra06.htm',
        'cbyra_2009.htm',
        'corsica_2005.htm',
        'cryc_2005.htm',
        'dick_tennerstedt.htm',
        'dues2002.html',
        'edith_r.htm',
        'flaherty.htm',
        'fphp06.htm',
        'garnet_imaging.htm',
        'giys_2009_nor.htm',
        'giys_2010_1.htm',
        'mastpart.html',
        'meeting05.htm',
        'officer.html',
        'oxford_summer2007.htm',
        'peng_intls_07_photo.htm',
        'plan_sale.htm',
        'slpf_sep07.htm',
        'swag.htm',
        'wanted1.html',
        'welcome.html',
        'ApleyAustin.htm',
        'CBYRA.htm',
        'ICPFR 2010_photos.htm',
        'Julie Cox.htm',
        'John_Thompson.htm',
        '10schedule (2).html',
        '07schedule.html',
        '20schedule.html',
        '2021schedule.html',
        '2022schedule.html'
    ]
    
    # PDF files to migrate (yearbooks and important documents)
    pdf_files = [
        '1955.pdf',
        '1957.pdf', 
        '1958.pdf',
        '1959.pdf',
        '1960.pdf',
        '1962.pdf',
        '1989_Intls.pdf',
        '2013_Penguin Natls NOR  2.pdf',
        '2013_TAYC_Summer.pdf',
        'NOR_Penguin_Spring_2011.pdf',
        '2010_PRSA_NOR.pdf',
        '2011 Classic Sailboats-Schedule.doc',
        '2011 Classic Wooden Sailboat Race - NOR.doc',
        '2011 INTERNATIONAL PENGUIN CHAMPIONSHIP SI.doc',
        '2011 INTERNATIONAL PENGUIN CHAMPIONSHIP SI_r1.doc',
        '2011 INTERNATIONAL PENGUIN CHAMPIONSHIP SI_r2.doc',
        '2011 INTL Penguin NOTICE OF RACE.doc',
        '2012 INTL Penguin NOTICE OF RACE.pdf',
        '2012 Penguin Internationals Summary_1.htm',
        '2012_CRYC Annual Regatta.pdf',
        '2012_Heritage Regatta.htm',
        '2012_Minutes of IPCDA Annual Meeting.pdf',
        '2012_TAYC_Summer One Design NOR.pdf',
        '2012_intls_results.pdf',
        '2012_intls_results.xlsx',
        '2013 MRYC Annual SI.pdf',
        '2013_Penguin Natls NOR  2.pdf',
        '2013_TAYC_Summer.pdf',
        '2014_CRYC Penguin Internationals.pdf',
        '2014_TCPFR.pdf',
        '2015_TAYC_PenguinFrostbiteNORpdf.pdf',
        '2016_TCPFR Trippes Creek Penguin Frostbite Regatta.doc',
        '2017_TCPFR Trippes Creek Penguin Frostbite Regatta - NOR.htm',
        '2018_TCPFR Trippes Creek Penguin Frostbite Regatta - NOR.htm',
        '2019 Comet and Penguin Invitational SI.pdf',
        '2019 MRYC One Design NOR rev2.pdf',
        '2019_TAYC Atlantic Coast.htm',
        '2019_TAYCPenguin and Comet Frostbite.htm',
        '2021 Jr Waiver.doc',
        '2021AlbacoreandFriendsNORa.pdf',
        '2021SpringInvitationalNOR.pdf',
        '2021_CRYC Annual Regatta NOR.doc',
        '2021_Cambridge_NoticeofRaceCBYRA.pdf',
        '2021_Cambridge_SIABRFleet.docx.pdf',
        '2021_CRYC_Turkey Trot_NOR.htm',
        '2021_GIYS_nor.htm',
        '2022 GIYS Comet and Penguin Invitational.docx',
        '2022 Turkey Trotl NOR.docx',
        '2022_TAYC Frostbite.docx',
        '2023 GIYS Comet and Penguin Invitational.pdf',
        '2023 Turkey Trotl NOR.htm',
        '2023_CRYC Annual Regatta NOR.htm',
        '2024 TAYC Annual.docx',
        '2024_NORPenguinInternationalRegatta.pdf',
        '2025_Beachwood_beach.jpeg',
        '2025_Cambridge.htm',
        '2025_Corsica Annual NOR.htm',
        '2025_Intls_NOR.htm',
        '2025_Intls_NOR.pdf.htm',
        '2025_TAYC Annual.docx',
        'Beachwood_NOR Penguin Revival 2023.pdf',
        'turkeytrot 2024 NOR.docx'
    ]
    
    migrated_count = 0
    skipped_count = 0
    
    print("Starting migration of high-priority missing content...")
    print(f"Legacy path: {legacy_path}")
    print(f"Jekyll archive path: {jekyll_archive_path}")
    
    # Migrate HTML/HTM files
    for filename in high_priority_files:
        if filename in exclude_files:
            print(f"Skipping excluded file: {filename}")
            skipped_count += 1
            continue
            
        legacy_file = os.path.join(legacy_path, filename)
        jekyll_file = os.path.join(jekyll_archive_path, filename)
        
        if os.path.exists(legacy_file) and not os.path.exists(jekyll_file):
            try:
                shutil.copy2(legacy_file, jekyll_file)
                print(f"Migrated: {filename}")
                migrated_count += 1
            except Exception as e:
                print(f"Error migrating {filename}: {e}")
        elif os.path.exists(jekyll_file):
            print(f"Already exists: {filename}")
        else:
            print(f"Not found in legacy: {filename}")
    
    # Migrate PDF files
    for filename in pdf_files:
        legacy_file = os.path.join(legacy_path, filename)
        jekyll_file = os.path.join(jekyll_archive_path, filename)
        
        if os.path.exists(legacy_file) and not os.path.exists(jekyll_file):
            try:
                shutil.copy2(legacy_file, jekyll_file)
                print(f"Migrated PDF: {filename}")
                migrated_count += 1
            except Exception as e:
                print(f"Error migrating PDF {filename}: {e}")
        elif os.path.exists(jekyll_file):
            print(f"PDF already exists: {filename}")
        else:
            print(f"PDF not found in legacy: {filename}")
    
    print(f"\nMigration complete!")
    print(f"Files migrated: {migrated_count}")
    print(f"Files skipped (excluded): {skipped_count}")

if __name__ == "__main__":
    migrate_files()

