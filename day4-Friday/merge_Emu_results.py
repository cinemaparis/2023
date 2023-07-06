import argparse
import csv
import os.path
import re

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg



def argument_parser():
    parser = argparse.ArgumentParser(prog = "merge_Emu_results.py", description="Merge Emu results files - simply specify files via the command line")
    parser.add_argument("--output", default = "output.tsv", help="Output filename", type=str)
    parser.add_argument('files', nargs='+', help = "Emu .tsv files to be merged", type=lambda x: is_valid_file(parser, x))
    return parser.parse_args()

if __name__=='__main__':
    args = argument_parser()
    print("\nmerge_Emu_results.py\n")
        
    print(f"Now merging {len(args.files)} files....\n")

    metadata_per_taxid = {}
    abundances_per_taxid = {}
    
    header_metadata = []
    sample_names = {}
    
    merge_files = args.files
    # merge_files = args.files[0:1]
    for f in merge_files:
        f_basename = os.path.basename(f)
        match_fn_component = re.search(r'(^.+)_rel-abundance.tsv', f_basename)
        assert(match_fn_component)
        assert(len(match_fn_component.groups())>=1)
        sample_name = match_fn_component.group(1)
        sample_names[sample_name] = 1
        
        with open(f) as fd:
            print ("\t" + f + " => " + sample_name + "\n")
            rd = csv.reader(fd, delimiter="\t")
            header = next(rd)
            assert(header[0] == "tax_id")
            assert(header[1] == "abundance")
            
            header_metadata = header[2:len(header)]
            
            for row in rd:
                tax_id = row[0]
                abundance = row[1]
                metadata = row[2:len(row)]
                assert(len(header_metadata) == len(metadata))
                metadata_dict = dict(zip(header_metadata, metadata))
                if not tax_id in metadata_per_taxid:
                    metadata_per_taxid[tax_id] = metadata_dict
                if not tax_id in abundances_per_taxid:
                    abundances_per_taxid[tax_id] = {}
                abundances_per_taxid[tax_id][sample_name] = abundance
                
    # print(", ".join(metadata_per_taxid.keys()))
    
    sample_names = list(sample_names.keys())
    with open(args.output, 'w') as csvout:
        csv_out = csv.writer(csvout, delimiter="\t")        
        header_row = ['tax_id'] + list(map(lambda x: "" + x, sample_names)) + header_metadata
       
        csv_out.writerow(header_row)
        for tax_id in abundances_per_taxid.keys():
            output_row = [tax_id] + list(map(lambda sample_name: abundances_per_taxid[tax_id][sample_name] if(sample_name in abundances_per_taxid[tax_id]) else 0, sample_names)) + list(map(lambda metadata_field: metadata_per_taxid[tax_id][metadata_field], header_metadata))
            csv_out.writerow(output_row)
            
    # print(abundances_per_taxid)
    # print(abundances_per_taxid["907"]["SRR14307925.fastq"])
    # print("\n")
    print("Done - generated output file " + args.output + ".\n")

