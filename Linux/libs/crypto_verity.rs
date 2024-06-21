/*
 * crypto_verity.rs
 *
 * Copyright 2024 Thomas Castleman <batcastle@draugeros.org>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 *
 */
//Imprort any needed libs
use std::env;
use std::fs;
use std::path::Path;
// use std::vec;
use std::process::exit;
use std::str;
use std::collections::HashMap;

// Define global variables
const _DPKG_CACHE: &str= "/var/lib/dpkg/info";


// Define private functions
fn bytes_to_str(byte_vec: Vec<u8>) -> String
{
    let output = match String::from_utf8(byte_vec) {
        Ok(v) => v,
        Err(e) => panic!("Invalid UTF-8 sequence: {}", e),
    };
    return output;
}


fn determine_package_manager () -> char
{
    /*
        Return values and cooralted package manager:
            - A: apt
            - D: dnf
            - E: eopkg
            - N: nix
            - P: pacman
            - Z: zypper
    */
    // To start off, we need to access environment variables
    let binding = env::var("PATH").expect("REASON");
    // Parse it
    let path = binding.split(":");
    let mut package_manager = "";
    // Iterate over our $PATH variable
    let mut flag = 0;
    for each in path
    {
        let iter = fs::read_dir(each).expect("REASON");
        for each1 in iter
        {
            let entry = each1.expect("REASON");
            let name = entry.file_name();
            if name.to_ascii_lowercase() == "apt"
            {
                if Path::new(_DPKG_CACHE).exists()
                {
                    package_manager = "apt";
                    flag = 1;
                    break;
                }

            }
        }
        if flag == 1
        {
            break;
        }
    }
    // Convert our string to a char and return that.
    if package_manager == "apt"
    {
        return 'A';
    }
    else if package_manager == "dnf"
    {
        return 'D';
    }
    else if package_manager == "eopkg"
    {
        return 'E';
    }
    else if package_manager == "nix"
    {
        return 'N';
    }
    else if package_manager == "pacman"
    {
        return 'P';
    }
    else if package_manager == "zypper"
    {
        return 'Z';
    }
    else
    {
        return ' ';
    }

}


// Define public functions
// Load MD5 sums into memory
pub fn load_md5s() -> HashMap<String, String>
{
    //Determine package manager
    let result = determine_package_manager();
    let mut md5_sums = HashMap::new();
    // Load MD5 sums for Apt
    if result == 'A'
    {
        let iter = fs::read_dir(_DPKG_CACHE).expect("REASON");
        for each1 in iter
        {
            let entry = each1.expect("REASON");
            let binding = entry.file_name().into_string().expect("REASON");
            let binding: Vec<&str> = binding.split(".").collect();
            let file_type = binding[binding.len() - 1];
            if file_type == "md5sums"
            {
                let contents = bytes_to_str(fs::read(entry.path()).expect("REASON"));
                let contents_vec: Vec<_> = contents.split('\n').collect();
                for each in contents_vec
                {
                    if each == ""
                    {
                        continue;
                    }
                    let add_on: Vec<_> = each.split("  ").collect();
                    md5_sums.insert(add_on[1].to_owned(), add_on[0].to_owned());
                }
            }
        }
    }
    else
    {
        println!("MD5 Sum loading not implemented for package managers other than `apt' yet.");
        exit(1);
    }
    return md5_sums;
}


// Load MD5 sums into memory
pub fn load_conffiles() -> Vec<String>
{
    //Determine package manager
    let result = determine_package_manager();
    let mut conffiles: Vec<String> = Vec::new();
    // Load MD5 sums for Apt
    if result == 'A'
    {
        let iter = fs::read_dir(_DPKG_CACHE).expect("REASON");
        for each1 in iter
        {
            let entry = each1.expect("REASON");
            let binding = entry.file_name().into_string().expect("REASON");
            let binding: Vec<&str> = binding.split(".").collect();
            let file_type = binding[binding.len() - 1];
            if file_type == "conffiles"
            {
                let contents = bytes_to_str(fs::read(entry.path()).expect("REASON"));
                let contents_vec: Vec<_> = contents.split('\n').collect();
                for each in contents_vec
                {
                    if each == ""
                    {
                        continue;
                    }
                    conffiles.push(each.to_owned());
                }
            }
        }
    }
    else
    {
        println!("Conf File loading not implemented for package managers other than `apt' yet.");
        exit(1);
    }
    return conffiles;
}


pub fn has_diversion(file_path: String) -> bool
{
    let mut split_path: Vec<_> = file_path.split("/").collect();
    split_path = split_path[split_path.len() - 1].split(".").collect();
    let file_name = split_path[0];
    let extension = split_path[split_path.len() - 1];
    split_path = file_path.split("/").collect();
    split_path = split_path[..split_path.len() - 1].to_vec();
    let mut path: String = "".to_string();
    for each in split_path
    {
        path = path.clone() + "/" + each;
    }
    let iter = fs::read_dir(path).expect("REASON");
    for each1 in iter
    {
            let entry = each1.expect("REASON");
            let binding = entry.file_name().into_string().expect("REASON");
            if binding.contains(file_name)
            {
                if binding.contains("orig")
                {
                    if binding.contains(extension)
                    {
                        return true;
                    }
                }
            }
    }
    return false;
}


fn main ()
{
    let conf_files = load_conffiles();
    println!("Conf Files loaded!");
    for each in conf_files
    {
        print!("{}: ", each);
        if has_diversion(each)
        {
            println!("HAS DIVERSION!");
        }
        else
        {
            println!("NO DIVERSION!");
        }
    }
}
