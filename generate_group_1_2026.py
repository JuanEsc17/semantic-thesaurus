import json

# Translation dictionary mapping Spanish symbol definitions to standardized English
# following the terminology of TTPS 2024 / LIFIA LEL datasets

translations = [
    {
        "name": "General Administrator",
        "type": "Subject",
        "notion": "User who manages the registration of system users, particularly medical managers.",
        "impact": "The general administrator registers medical managers."
    },
    {
        "name": "Administrative Staff",
        "type": "Subject",
        "notion": "Staff member of the central laboratory who registers themselves with first name, last name, phone number, and email, and manages the administrative procedures for the study.",
        "impact": "The administrative staff issues the study budget. The administrative staff records whether the health insurance authorized or rejected the study. The administrative staff uploads the raw data received from Korea. The administrative staff schedules the pickup of the sample set with FedEx. The administrative staff cannot unregister themselves or delete their information."
    },
    {
        "name": "Bioinformatician",
        "type": "Subject",
        "notion": "Member of the bioinformatics team who analyzes raw data; registers with first name, last name, email, and phone number. The team shares a single email address.",
        "impact": "The bioinformatician receives a notification at the team email when a study transitions to Under Bioinformatics Analysis. The bioinformatician claims a study and sets it to Under Bioinformatician Analysis. The bioinformatician chooses a gene and selects identified variants. The bioinformatician uploads variants into the study. The bioinformatician sees urgent Pompe studies first. The bioinformatician cannot unregister themselves or delete their information."
    },
    {
        "name": "Medical Manager",
        "type": "Subject",
        "notion": "Physician with additional administrative privileges; registered by the general administrator with the same information as a physician.",
        "impact": "The medical manager creates coupons and defines their discount percentage. The medical manager assigns coupons to physicians. The medical manager registers pathologies. The medical manager defines the cardinal symptom and secondary symptoms of each pathology. The medical manager modifies a pathology."
    },
    {
        "name": "Physician",
        "type": "Subject",
        "notion": "Healthcare professional who registers with license number, medical specialties, first name, last name, phone number, and email, and refers patients from the initial consultation. Synonyms: treating physician, referring physician.",
        "impact": "The physician registers the patient if they do not exist. The physician registers the patient's study. The physician records the medical history using the audio transcriber. The physician logs symptoms using SNOMED. The physician logs family members and submits the familiogram. The physician selects genes and can manually add genes. The physician indicates whether secondary findings are requested. The physician assigns coupons to patients. The physician requests reanalysis. The physician receives an email when the result is uploaded. The system assumes the physician's license number is valid. The physician cannot cancel an appointment or unregister themselves."
    },
    {
        "name": "Patient",
        "type": "Subject",
        "notion": "Individual for whom a study is ordered; accesses the system with username and password. If the patient is a minor, the parent performs the process.",
        "impact": "The patient changes password upon first login. The patient pays the budget or awaits health insurance authorization. The patient applies a coupon when paying. The patient chooses an appointment at an extraction center. The patient cancels the appointment. The patient forfeits the payment if they miss five appointments. The patient downloads the result. The patient files a legal claim and its supporting documentation if the health insurance rejects the study. The patient queries the chatbot. The patient cannot unregister themselves or delete their information."
    },
    {
        "name": "Transporter",
        "type": "Subject",
        "notion": "Courier who transports samples from extraction centers to the central laboratory; there is one per province.",
        "impact": "The transporter receives the daily route order. The transporter logs pickup at each extraction center. The transporter logs arrival at the central laboratory. The transporter cannot modify the daily route order."
    },
    {
        "name": "Bioinformatics API",
        "type": "Object",
        "notion": "External module providing the genes for each pathology, secondary finding genes, variants for each gene, and their classification.",
        "impact": "The system queries the Bioinformatics API to retrieve genes. The system queries the Bioinformatics API to list variants of a gene."
    },
    {
        "name": "Coupons API",
        "type": "Object",
        "notion": "External module that generates coupons with QR codes and validates their active status.",
        "impact": "The system requests a coupon from the Coupons API when created by the medical manager. The system verifies whether the coupon is currently valid. The system notifies that the coupon was redeemed so it expires."
    },
    {
        "name": "Familiogram API",
        "type": "Object",
        "notion": "External module that receives family relationships and returns the familiogram in PDF format.",
        "impact": "The system sends kinship relationships to the Familiogram API. The system associates the received PDF with the patient."
    },
    {
        "name": "Health Insurance API",
        "type": "Object",
        "notion": "External module containing the list of health insurances and their coverage percentages.",
        "impact": "The system queries the Health Insurance API to display coverage to the patient."
    },
    {
        "name": "Route Optimization API",
        "type": "Object",
        "notion": "Potential external module that sequences the stops for the daily route order.",
        "impact": "The system sends destination addresses for the transporter and receives the optimized route sequence."
    },
    {
        "name": "Ministry of Health API",
        "type": "Object",
        "notion": "External module that receives the CSV file and returns the Ministry Authorization.",
        "impact": "The system sends the CSV file to the Ministry of Health API without administrative staff intervention. The system associates the received PDF with the studies in the sample set."
    },
    {
        "name": "Ministry Authorization",
        "type": "Object",
        "notion": "PDF permit allowing the export of patient samples in the sample set to Korea; must match the samples in the shipment parcel.",
        "impact": "The system associates the Ministry Authorization with each study in the sample set. The Ministry Authorization travels with the sample set to Korea."
    },
    {
        "name": "Notification",
        "type": "Object",
        "notion": "In-system notification, complementary to email, that informs users of pending actions.",
        "impact": "The system displays a list of notifications to the user."
    },
    {
        "name": "Telegram Bot",
        "type": "Object",
        "notion": "Central laboratory account number that receives a message whenever a sample is collected.",
        "impact": "The extraction center sends a message to the Telegram bot. The system transitions the study to Ready for Pickup upon receiving the message."
    },
    {
        "name": "Extraction Center",
        "type": "Object",
        "notion": "Outsourced laboratory where the biological sample is collected; there are 100 nationwide and they do not operate directly within the system.",
        "impact": "The patient attends the extraction center at the scheduled appointment time. The extraction center informs the Telegram bot that the sample was collected."
    },
    {
        "name": "Chatbot",
        "type": "Object",
        "notion": "External conversational module answering patient inquiries about pathologies.",
        "impact": "The system forwards the inquiry to the chatbot and displays the answer."
    },
    {
        "name": "Verification Code",
        "type": "Object",
        "notion": "Code sent via email by the system to authenticate login from a new device.",
        "impact": "The system sends the verification code to the user's email when logging in from a new machine. The user enters the verification code to gain access."
    },
    {
        "name": "Informed Consent",
        "type": "Object",
        "notion": "Legal document printed, filled out, signed, and delivered by the patient (or parent); managed outside the system and not stored electronically within it.",
        "impact": "The system sends the informed consent to the patient upon booking an appointment."
    },
    {
        "name": "CSV File",
        "type": "Object",
        "notion": "Structured file listing the patients included in the sample set, required by the Ministry of Health.",
        "impact": "The system automatically generates the CSV file when the sample set is closed. The system associates the CSV file with the studies in the sample set."
    },
    {
        "name": "Coupon",
        "type": "Object",
        "notion": "Discount voucher with QR or numeric code created by the medical manager; stacks with health insurance coverage.",
        "impact": "The physician assigns the coupon to a patient. The patient applies the coupon during payment. The Coupons API expires the coupon upon redemption."
    },
    {
        "name": "Raw Data",
        "type": "Object",
        "notion": "Genomic text file containing A, C, T, and G nucleotide sequences received from Korea; simulated in the current prototype phase.",
        "impact": "The administrative staff uploads the study's raw data. The bioinformatician analyzes the raw data to discover variants."
    },
    {
        "name": "Legal Claim",
        "type": "Object",
        "notion": "Administrative or legal complaint filed by the patient with favorable judicial documentation in PDF when the health insurance denies coverage.",
        "impact": "The patient uploads the legal claim linked to the study. The system enables study reauthorization."
    },
    {
        "name": "Medical Specialty",
        "type": "Object",
        "notion": "Standardized medical discipline chosen by the physician during registration; selection list must be as comprehensive as possible.",
        "impact": "The physician selects their specialties from the standardized list."
    },
    {
        "name": "Study",
        "type": "Object",
        "notion": "Clinical exome sequencing examination analyzing patient DNA to detect variants across selected genes. Synonym: sample.",
        "impact": "The physician registers the study. The study progresses through discrete states along a unified workflow. The study has a base price of 500 USD up to 5 genes and 30 USD per additional gene. The study rolls back to Resampling Required if the sample is insufficient. The system logs the tube volume in milliliters."
    },
    {
        "name": "Family Member",
        "type": "Object",
        "notion": "Relative of the patient, recorded with kinship relationship, name, symptoms, and prior diagnosis if available.",
        "impact": "The physician records each family member of the patient. The system forwards family records to the Familiogram API."
    },
    {
        "name": "Familiogram",
        "type": "Object",
        "notion": "Pedigree chart in PDF format illustrating the patient's family relationships and inheritance pattern. Synonym: genogram.",
        "impact": "The Familiogram API returns the pedigree chart. The system links the familiogram to the patient record."
    },
    {
        "name": "Gene",
        "type": "Object",
        "notion": "Segment of DNA encoding a functional protein; linked to a specific pathology.",
        "impact": "The physician selects target genes for analysis. The bioinformatician selects the gene to record identified variants."
    },
    {
        "name": "Secondary Finding",
        "type": "Object",
        "notion": "Additional panel of actionable genes unrelated to the suspected pathology that the physician may optionally request for analysis.",
        "impact": "The physician indicates whether secondary findings are requested. The Bioinformatics API reports the corresponding panel genes."
    },
    {
        "name": "Medical Record",
        "type": "Object",
        "notion": "Clinical health summary recorded by the physician when registering the patient. Synonym: clinical history.",
        "impact": "The physician dictates the medical history and the audio transcriber converts it to text."
    },
    {
        "name": "Tracking Map",
        "type": "Object",
        "notion": "Geographical visualization displaying the real-time transit location of a patient's sample with the transporter.",
        "impact": "The system displays the current sample position on the tracking map."
    },
    {
        "name": "Sample",
        "type": "Object",
        "notion": "Biological blood specimen drawn from the patient for genetic study.",
        "impact": "The patient provides the biological sample at the extraction center. The transporter delivers the sample to the central laboratory. The system aggregates samples into sample sets. The system triggers resampling if the tube contains less than 2 milliliters."
    },
    {
        "name": "Health Insurance",
        "type": "Object",
        "notion": "Healthcare provider or insurer offering partial or full coverage for the study budget.",
        "impact": "The health insurance authorizes or denies the study coverage. The health insurance pays the study fee once authorized."
    },
    {
        "name": "Extraction Order",
        "type": "Object",
        "notion": "Formal appointment voucher specifying date, time, and center details provided to the patient.",
        "impact": "The system issues the extraction order to the patient upon booking an appointment."
    },
    {
        "name": "Daily Route Order",
        "type": "Object",
        "notion": "Fixed, optimized itinerary of extraction centers delivered to the transporter each morning; not issued on weekends or holidays.",
        "impact": "The system generates the daily route order using the Route Optimization API. The transporter cannot alter the daily route order."
    },
    {
        "name": "Pathology",
        "type": "Object",
        "notion": "Lysosomal storage disease diagnosed by the laboratory (Fabry, Pompe, Mucopolysaccharidosis I, Gaucher, ASMD), characterized by one cardinal symptom and secondary symptoms.",
        "impact": "The medical manager defines and updates the pathology. The physician selects the pathology as presumptive diagnosis. The system cross-validates reported symptoms against the pathology."
    },
    {
        "name": "Urgent Pompe",
        "type": "Object",
        "notion": "Critical Pompe disease study for an infant under 4 months of age, permitted to ship immediately without waiting for a full sample set.",
        "impact": "The system immediately closes the sample set upon arrival of an urgent Pompe study. The bioinformatician sees urgent Pompe studies prioritized at the top of their queue."
    },
    {
        "name": "Budget",
        "type": "Object",
        "notion": "Total examination fee, including blood extraction, payable as a single lump sum.",
        "impact": "The administrative staff generates the budget. The patient pays the budget or health insurance coverage applies. The system records the financial transaction."
    },
    {
        "name": "Reminder",
        "type": "Object",
        "notion": "Automated email notification sent for each booked appointment specifying date, time, and the 5-absence threshold.",
        "impact": "The system dispatches the reminder email to the patient upon appointment booking."
    },
    {
        "name": "Result",
        "type": "Object",
        "notion": "Formal diagnostic PDF detailing positive/negative status and specific genetic variants detected for the patient.",
        "impact": "The system notifies the physician and patient via email when the result is uploaded. The patient downloads the diagnostic report."
    },
    {
        "name": "Sample Set",
        "type": "Object",
        "notion": "Consolidated batch of 10 samples shipped abroad to Korea; shipped incomplete only for urgent Pompe cases.",
        "impact": "The system compiles the sample set as samples arrive. The system closes the sample set upon reaching 10 samples or when an urgent Pompe sample arrives. The administrative staff schedules courier pickup. The system prohibits adding further samples once closed."
    },
    {
        "name": "SNOMED",
        "type": "Object",
        "notion": "International standardized clinical terminology system used for coding medical symptoms.",
        "impact": "The physician searches for symptoms using SNOMED autocomplete during data entry."
    },
    {
        "name": "Symptom",
        "type": "Object",
        "notion": "Clinical sign or symptom reported for the patient or relative, coded using SNOMED. Categorized as cardinal symptom or secondary symptom.",
        "impact": "The physician records patient symptoms. The system verifies symptoms against presumptive pathology criteria."
    },
    {
        "name": "Cardinal Symptom",
        "type": "Object",
        "notion": "Primary hallmark symptom defining a specific pathology.",
        "impact": "The medical manager designates the cardinal symptom. Presence of a cardinal symptom qualifies the patient for registration."
    },
    {
        "name": "Secondary Symptom",
        "type": "Object",
        "notion": "Supporting clinical symptom associated with a pathology.",
        "impact": "Two secondary symptoms satisfy registration criteria when no cardinal symptom is identified."
    },
    {
        "name": "Audio Transcriber",
        "type": "Object",
        "notion": "Speech-to-text automated tool that transcribes physician dictation into written clinical records.",
        "impact": "The physician uses the audio transcriber to record the medical history."
    },
    {
        "name": "Appointment",
        "type": "Object",
        "notion": "15-minute scheduled extraction time slot at an extraction center for an individual, available Monday through Friday from 9 to 18, excluding holidays.",
        "impact": "The patient selects an open appointment slot on the interactive map. The patient cancels an appointment. The system delivers a reminder email for each appointment."
    },
    {
        "name": "Variant",
        "type": "Object",
        "notion": "Patient DNA nucleotide variation differing from reference genome, classified as pathogenic, benign, harmless, or VUS.",
        "impact": "The bioinformatician selects the variant from the gene candidate list. The genetic diagnosis is positive if the identified variant is pathogenic."
    },
    {
        "name": "VUS",
        "type": "Object",
        "notion": "Variant of Uncertain Significance; a genomic alteration lacking sufficient clinical evidence to classify as pathogenic or benign.",
        "impact": "The Bioinformatics API may classify an identified variant as VUS."
    },
    {
        "name": "Assemble Sample Set",
        "type": "Verb",
        "notion": "Grouping biological samples into 10-specimen batches to optimize international shipping costs.",
        "impact": "The system adds incoming samples to the current sample set upon arrival at the central laboratory. The system closes the sample set at 10 samples or immediately upon receiving an urgent Pompe study."
    },
    {
        "name": "Cancel Appointment",
        "type": "Verb",
        "notion": "Releasing a previously booked extraction time slot.",
        "impact": "The patient cancels the appointment. The physician is restricted from canceling appointments."
    },
    {
        "name": "Upload Result",
        "type": "Verb",
        "notion": "Entering detected genetic variants into the study record to issue the diagnostic report to physician and patient.",
        "impact": "The bioinformatician enters the variants into the study. The study transitions to Result Uploaded. The system dispatches email notifications to physician and patient."
    },
    {
        "name": "Register Study",
        "type": "Verb",
        "notion": "Initiating a new exome sequencing order for a registered patient.",
        "impact": "The physician selects the patient, target genes, and secondary finding preferences. The study transitions to Created."
    },
    {
        "name": "Register Patient",
        "type": "Verb",
        "notion": "Enrolling a new patient by entering mandatory demographic and clinical data, excluding optional familiogram.",
        "impact": "The physician enters ID number, name, surname, phone, email, birthdate, presumptive diagnosis, medical history, symptoms, and suspicion type. The system cross-validates symptoms against the selected pathology. The system dispatches login credentials to the patient via email."
    },
    {
        "name": "Log In",
        "type": "Verb",
        "notion": "Authenticating user identity and granting authorized access into the system using credentials.",
        "impact": "The user supplies username and password. The system prompts for a verification code when accessed from an unrecognized machine."
    },
    {
        "name": "Pay Budget",
        "type": "Verb",
        "notion": "Remitting payment for the examination fee in a single lump-sum transaction.",
        "impact": "The patient pays the budget fee and may redeem a coupon. The system records the payment. The patient is granted authorization to book an appointment."
    },
    {
        "name": "Reanalyze Study",
        "type": "Verb",
        "notion": "Sequencing and evaluating different genes from previously extracted DNA without drawing a new patient blood sample.",
        "impact": "The physician requests study reanalysis. The reanalysis proceeds using the existing study sample record."
    },
    {
        "name": "Resample",
        "type": "Verb",
        "notion": "Collecting a replacement blood sample from the patient when the previous specimen is unusable, at no additional charge to the patient.",
        "impact": "The system notifies physician and patient via email. The study rolls back to Resampling Required. The patient books a new appointment under the same study order."
    },
    {
        "name": "Pick Up Sample Set",
        "type": "Verb",
        "notion": "Releasing the sealed sample set container to the international courier for overseas transit to Korea.",
        "impact": "The administrative staff schedules the pickup date, time, and consignment details. The system updates the status of the sample set and contained studies to In Transit to Korea."
    },
    {
        "name": "Book Appointment",
        "type": "Verb",
        "notion": "Reserving an extraction time slot at a preferred extraction center following payment or insurance authorization.",
        "impact": "The patient chooses an extraction facility on the map and selects an available slot. The system dispatches extraction order, informed consent, and reminder documentation."
    },
    {
        "name": "Authorized",
        "type": "State",
        "notion": "Study status after approval by the health insurance, treated as fully paid.",
        "impact": "The administrative staff marks the study as Authorized. The system notifies the patient and enables appointment booking."
    },
    {
        "name": "Created",
        "type": "State",
        "notion": "Initial study status following registration by physician, awaiting payment or insurance verification.",
        "impact": "The patient pays the budget and is cleared to book an appointment. The study transitions to Appointment Booked when scheduled. The study transitions to Pending Authorization if the patient selects insurance coverage. The study reverts to Created if the patient misses five scheduled appointments, requiring payment renewal."
    },
    {
        "name": "Under Bioinformatician Analysis",
        "type": "State",
        "notion": "Study status when claimed by a specific bioinformatician for variant evaluation.",
        "impact": "The bioinformatician uploads identified variants and the study transitions to Result Uploaded."
    },
    {
        "name": "Under Bioinformatics Analysis",
        "type": "State",
        "notion": "Study status once raw genomic sequencing data is received from Korea and queued for the bioinformatics department. Synonym: in bioinformatics area.",
        "impact": "The administrative staff uploads raw sequencing data and the study transitions to Under Bioinformatics Analysis. A bioinformatician claims the study and sets it to Under Bioinformatician Analysis."
    },
    {
        "name": "In Transit to Central Laboratory",
        "type": "State",
        "notion": "Study status while its collected specimen is in transit in the transporter's custody.",
        "impact": "The transporter logs central arrival and the study transitions to At Central Laboratory."
    },
    {
        "name": "Awaiting Pickup",
        "type": "State",
        "notion": "Study status when its enclosing sample set is sealed and awaiting courier collection.",
        "impact": "The administrative staff schedules courier collection and the study transitions to In Transit to Korea at the designated time."
    },
    {
        "name": "At Central Laboratory",
        "type": "State",
        "notion": "Study status when the biological sample has arrived at the central facility.",
        "impact": "The system incorporates the sample into an active sample set. The system closes the sample set and the study transitions to Awaiting Pickup."
    },
    {
        "name": "In Transit to Korea",
        "type": "State",
        "notion": "Study and sample set status during international shipment following courier handover.",
        "impact": "The administrative staff uploads raw sequencing data upon receipt and the study transitions to Under Bioinformatics Analysis."
    },
    {
        "name": "Ready for Pickup",
        "type": "State",
        "notion": "Study status after the blood specimen has been successfully collected at the extraction center.",
        "impact": "The transporter logs collection and the study transitions to In Transit to Central Laboratory."
    },
    {
        "name": "Pending Authorization",
        "type": "State",
        "notion": "Study status awaiting coverage determination from the designated health insurance provider.",
        "impact": "The administrative staff records approval and the study transitions to Authorized. The administrative staff records denial and the study transitions to Rejected."
    },
    {
        "name": "Rejected",
        "type": "State",
        "notion": "Study status following insurance coverage denial.",
        "impact": "The patient uploads a legal claim and appeals for reauthorization. The study reverts to Pending Authorization."
    },
    {
        "name": "Resampling Required",
        "type": "State",
        "notion": "Study status when the collected sample is unusable due to insufficient volume under 2 ml or degraded DNA.",
        "impact": "The patient schedules a replacement appointment without re-paying. The study transitions to Appointment Booked."
    },
    {
        "name": "Result Uploaded",
        "type": "State",
        "notion": "Study status when final genetic findings and diagnostic report are available in the system.",
        "impact": "The system delivers notification emails to both physician and patient."
    },
    {
        "name": "Appointment Booked",
        "type": "State",
        "notion": "Study status with a confirmed extraction appointment reserved.",
        "impact": "The patient attends and the system sets the study to Ready for Pickup upon receiving the Telegram bot notification. If the patient misses 1 to 4 times, they schedule another slot. If the patient misses 5 times, the study reverts to Created."
    }
]

out_en = "domain/lel_ttps_group_1_2026.json"
with open(out_en, "w", encoding="utf-8") as f:
    json.dump(translations, f, indent=4, ensure_ascii=False)

print(f"Generated {len(translations)} standardized English LEL entries in {out_en}!")

